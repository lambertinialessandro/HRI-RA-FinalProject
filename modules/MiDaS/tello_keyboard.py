# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.


# %matplotlib qt
# %matplotlib inline

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import cv2
import math
import time
import random

import keyboard
import schedule

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt

from djitellopy import Tello

from run import buildDeepMonocular

import platform
capture_api = None
input_idx = 0
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW

import sys
sys.path.append('../../')
from modules.drone.DroneModule import FakeDrone, DJITello


global state
state = True

dm = buildDeepMonocular(model_weights=None, model_type="dpt_hybrid", # midas_v21_small, dpt_hybrid
                        optimize=True, bits=1)

def get_rotation_matrix(orientation, axis='x'):
    c = math.cos(orientation)
    s = math.sin(orientation)

    rotation_matrix = None
    if axis == 'x':
        rotation_matrix = np.array(
            [[1, 0, 0],
             [0, c, -s],
             [0, s, c]])
    elif axis == 'y':
        rotation_matrix = np.array(
            [[c, 0, s],
             [0, 1, 0],
             [-s, 0, c]])
    elif axis == 'z':
        rotation_matrix = np.array(
            [[c, -s, 0],
             [s, c, 0],
             [0, 0, 1]])
    return rotation_matrix

def get_cmap(values, cmap_name='rainbow'):
    cmap = cm.get_cmap(cmap_name, 12)
    depth_values_normalized = values/max(values)
    return cmap(depth_values_normalized)

def get_3d_points_from_depthmap(depth_map, position=[0, 0, 0], z_orientation=0,
                                per_mil_to_keep=1):
    IMAGE_WIDTH = 30 # 256 # 960
    IMAGE_HEIGHT = 30 # 256 # 720

    H_FOV_DEGREES = 82.6
    H_FOV_RAD = math.radians(H_FOV_DEGREES)
    V_FOV_RAD = math.radians(IMAGE_HEIGHT/IMAGE_WIDTH*H_FOV_DEGREES)
    X_FOCAL = IMAGE_WIDTH / (2*math.tan(H_FOV_RAD/2))
    Y_FOCAL = IMAGE_HEIGHT / (2*math.tan(V_FOV_RAD/2))
    X_CENTER_COORDINATE = (0.5*IMAGE_WIDTH)
    Y_CENTER_COORDINATE = (0.5*IMAGE_HEIGHT)

    depth_width, depth_height = depth_map.shape
    x_depth_rescale_factor = depth_width / IMAGE_WIDTH
    y_depth_rescale_factor = depth_height / IMAGE_HEIGHT

    points_in_3d = np.array([])
    depth_values = np.array([])
    rotation_matrix = get_rotation_matrix(math.radians(z_orientation), axis="z")

    for x in range(IMAGE_WIDTH):
        for y in range(IMAGE_HEIGHT):

            # keep n per-mil points
            if random.randint(0, 999) >= per_mil_to_keep:
                continue

            x_depth_pos = int(x * x_depth_rescale_factor)
            y_depth_pos = int(y * y_depth_rescale_factor)
            depth_value = depth_map[x_depth_pos, y_depth_pos]

            # get 3d vector
            z_point = depth_value * (x - X_CENTER_COORDINATE) / X_FOCAL
            y_point = depth_value * (y - Y_CENTER_COORDINATE) / Y_FOCAL
            point_3d_before_rotation = np.array([depth_value, y_point, z_point])

            # projection in function of the orientation
            point_in_3d = np.matmul(rotation_matrix, point_3d_before_rotation
                                    ) + position
            points_in_3d = np.append(points_in_3d, point_in_3d)
            depth_values = np.append(depth_values, depth_value)

    return points_in_3d, depth_values

class Drone(FakeDrone):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.x = 0
        self.y = 0
        self.h = 0

        self.teta = 0
        self.c = math.cos(self.teta)
        self.s = math.sin(self.teta)

        self.story = np.array([[self.x, self.y, self.h, self.teta, 0]])

        self.camera = Tello.CAMERA_FORWARD

    def move_forward(self, value):
        super().move_forward(value)
        self.x = self.x + self.c * value
        self.y = self.y + self.s * value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 1]], axis=0)

    def move_back(self, value):
        super().move_backward(value)
        self.x = self.x + self.c * -value
        self.y = self.y + self.s * -value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 2]], axis=0)

    def move_left(self, value):
        super().move_left(value)
        self.x = self.x + self.s * value
        self.y = self.y + self.c * value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 3]], axis=0)

    def move_right(self, value):
        super().move_right(value)
        self.x = self.x + self.s * -value
        self.y = self.y + self.c * -value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 4]], axis=0)

    def rotate_clockwise(self, value):
        super().rotate_cw(value)
        self.teta = self.teta - math.radians(value)
        self.c = math.cos(self.teta)
        self.s = math.sin(self.teta)
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 5]], axis=0)

    def rotate_counter_clockwise(self, value):
        super().rotate_ccw(value)
        self.teta = self.teta + math.radians(value)
        self.c = math.cos(self.teta)
        self.s = math.sin(self.teta)
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 6]], axis=0)

    def move_up(self, value):
        super().move_up(value)
        self.h = self.h + value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 7]], axis=0)

    def move_down(self, value):
        super().move_down(value)
        self.h = self.h - value
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 8]], axis=0)

    def take_off(self):
        super().take_off()
        self.h = self.h + 100
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, -1]], axis=0)

    def land(self):
        super().land()
        self.h = self.h - 100
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, -2]], axis=0)

    def swap_video_direction(self):
        if self.camera == Tello.CAMERA_FORWARD:
            self.camera = Tello.CAMERA_DOWNWARD
        elif self.camera == Tello.CAMERA_DOWNWARD:
            self.camera = Tello.CAMERA_FORWARD
        super().set_video_direction(self.camera)

tello = Drone(input_idx=input_idx, capture_api=capture_api)

battery = tello.battery
height = tello.height
temperature = tello.temperature

def update_battery():
    global tello, battery
    battery = tello.battery
def update_height():
    global tello, height
    height = tello.height
def update_temperature():
    global tello, temperature
    temperature = tello.temperature

schedule.every(10).seconds.do(update_battery)
schedule.every(1).seconds.do(update_height)
schedule.every(5).seconds.do(update_temperature)

#tello.swap_video_direction()

points_in_3d = np.array([])
depth_values = np.array([])

tello.streamon()
frame = tello.frame
if frame is None:
    frame = out = np.zeros((256, 256, 3))
depth = dm.run_on_frame(frame)

per_mil_to_keep = 100
point_in_3d, depth_value = get_3d_points_from_depthmap(depth,
                                position=[tello.x, tello.y, tello.h],
                                z_orientation=tello.teta,
                                per_mil_to_keep=per_mil_to_keep)
points_in_3d = np.append(points_in_3d, point_in_3d)
points_in_3ds = points_in_3d.reshape([-1, 3])
depth_values = np.append(depth_values, depth_value)

max_projection_value = max(depth_values)
depth_values_normalized = depth_values/max_projection_value
colormap = get_cmap(depth_values_normalized)

def my_keyboard_hook(keyboard_event):
    try:
        global tello
        global state
        print("Name:", keyboard_event.name)
        print("Scan code:", keyboard_event.scan_code)
        print("Time:", keyboard_event.time)

        if keyboard_event.name == "t":
            tello.take_off()
        elif keyboard_event.name == "esc":
            tello.land()
            state = False
        elif keyboard_event.name == "w":
            tello.move_forward(30)
        elif keyboard_event.name == "s":
            tello.move_back(30)
        elif keyboard_event.name == "a":
            tello.move_left(30)
        elif keyboard_event.name == "d":
            tello.move_right(30)
        elif keyboard_event.name == "e":
            tello.rotate_clockwise(30)
        elif keyboard_event.name == "q":
            tello.rotate_counter_clockwise(30)
        elif keyboard_event.name == "r":
            tello.move_up(30)
        elif keyboard_event.name == "f":
            tello.move_down(30)
        elif keyboard_event.name == "1":
            tello.swap_video_direction()
    except:
        state = False

keyboard.on_press(my_keyboard_hook)

fig = plt.figure()
fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122, projection='3d')

cv2.namedWindow('drone', cv2.WINDOW_NORMAL)
cv2.resizeWindow('drone', 600,600)
cv2.namedWindow('depth', cv2.WINDOW_NORMAL)
cv2.resizeWindow('depth', 600,600)


try:
    time.sleep(2)
    start_T = time.time()
    while state:
        schedule.run_pending()

        frame = tello.frame
        if time.time() - start_T > 10.5:
            start_T = time.time()
            print("run_on_frame!")
            depth = dm.run_on_frame(frame)

            point_in_3d, depth_value = get_3d_points_from_depthmap(depth,
                                            position=[tello.x, tello.y, tello.h],
                                            z_orientation=tello.teta,
                                            per_mil_to_keep=per_mil_to_keep)
            points_in_3d = np.append(points_in_3d, point_in_3d)
            points_in_3ds = points_in_3d.reshape([-1, 3])
            depth_values = np.append(depth_values, depth_value)

            max_projection_value = max(depth_values)
            depth_values_normalized = depth_values/max_projection_value
            colormap = get_cmap(depth_values_normalized)

            ax2.clear()
            ax2.scatter(
                points_in_3ds[:, 0],
                points_in_3ds[:, 1],
                -points_in_3ds[:, 2],
                c=colormap,
                s=5
            )

        cv2.putText(frame, f"battery: {battery}", (10, 15), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"Height: {height}", (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"temperature: {temperature}", (10, 45), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)

        ax1.clear()

        c = math.cos(tello.story[-1, 3])
        s = math.cos(tello.story[-1, 3])
        ax1.quiver(tello.story[-1, 0], tello.story[-1, 1], tello.story[-1, 2],
                  c, s, 0,
                  length=10, normalize=True, color="black")
        ax1.plot(
            tello.story[:, 0],
            tello.story[:, 1],
            tello.story[:, 2],
            c="red"
        )
        plt.pause(0.5)

        cv2.imshow("drone", frame)
        cv2.imshow("depth", depth)
        key = cv2.waitKey(1)
finally:
    print("Terminating!")
    cv2.destroyAllWindows()
    keyboard.unhook_all()
    schedule.clear()
    plt.close(fig)
    tello.end()



# ii = input("ok? ")

# if ii == "ok":
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     for i in range(tello.story.shape[0]):
#         ax.clear()
#         c = math.cos(tello.story[i, 3])
#         s = math.cos(tello.story[i, 3])
#         ax.quiver(tello.story[i, 0], tello.story[i, 1], tello.story[i, 2],
#                   c, s, 0,
#                   length=10, normalize=True, color="black")
#         ax.plot(
#             tello.story[0:i+1, 0],
#             tello.story[0:i+1, 1],
#             tello.story[0:i+1, 2],
#             c="red"
#         )
#         plt.pause(0.5)


