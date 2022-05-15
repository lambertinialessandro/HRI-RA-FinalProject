# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.


# %matplotlib qt
# %matplotlib inline

import cv2
import math
import time

import keyboard
import schedule

import numpy as np
import matplotlib.pyplot as plt

from djitellopy import Tello

from run import buildDeepMonocular

global state
state = True

c = 0
dm = buildDeepMonocular(model_weights=None, model_type="midas_v21_small", # midas_v21_small, dpt_hybrid
                        optimize=True, bits=1)

class Drone(Tello):
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
        super().move_back(value)
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
        super().rotate_clockwise(value)
        self.teta = self.teta - math.radians(value)
        self.c = math.cos(self.teta)
        self.s = math.sin(self.teta)
        self.story = np.append(self.story, [[self.x, self.y, self.h, self.teta, 5]], axis=0)

    def rotate_counter_clockwise(self, value):
        super().rotate_counter_clockwise(value)
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

    def takeoff(self):
        super().takeoff()
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

tello = Drone()
tello.connect()

battery = tello.get_battery()
height = tello.get_height()
temperature = tello.get_temperature()

def update_battery():
    global tello, battery
    battery = tello.get_battery()
def update_height():
    global tello, height
    height = tello.get_height()
def update_temperature():
    global tello, temperature
    temperature = tello.get_temperature()

schedule.every(10).seconds.do(update_battery)
schedule.every(1).seconds.do(update_height)
schedule.every(5).seconds.do(update_temperature)

#tello.swap_video_direction()

tello.streamon()
frame_read = tello.get_frame_read()
frame = frame_read.frame
depth = dm.run_on_frame(frame)

def my_keyboard_hook(keyboard_event):
    try:
        global tello
        global state
        print("Name:", keyboard_event.name)
        print("Scan code:", keyboard_event.scan_code)
        print("Time:", keyboard_event.time)

        if keyboard_event.name == "t":
            tello.takeoff()
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
ax = fig.add_subplot(111, projection='3d')

cv2.namedWindow('drone', cv2.WINDOW_NORMAL)
cv2.resizeWindow('drone', 600,600)

try:
    time.sleep(2)
    while state:
        schedule.run_pending()
        # In reality you want to display frames in a seperate thread. Otherwise
        #  they will freeze while the drone moves.
        frame = frame_read.frame
        if c == 1000:
            c = 0
            print("run_on_frame!")
            depth = dm.run_on_frame(frame)

        cv2.putText(frame, f"battery: {battery}", (10, 15), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"Height: {height}", (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"temperature: {temperature}", (10, 45), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)

        ax.clear()
        c = math.cos(tello.story[-1, 3])
        s = math.cos(tello.story[-1, 3])
        ax.quiver(tello.story[-1, 0], tello.story[-1, 1], tello.story[-1, 2],
                  c, s, 0,
                  length=10, normalize=True, color="black")
        ax.plot(
            tello.story[:, 0],
            tello.story[:, 1],
            tello.story[:, 2],
            c="red"
        )
        plt.pause(0.5)

        cv2.imshow("drone", frame)
        cv2.imshow("depth", depth)
        key = cv2.waitKey(1)
        c = c + 1
finally:
    print("Terminating!")
    cv2.destroyAllWindows()
    keyboard.unhook_all()
    schedule.clear()
    plt.close(fig)
    tello.end()



ii = input("ok? ")

if ii == "ok":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(tello.story.shape[0]):
        ax.clear()
        c = math.cos(tello.story[i, 3])
        s = math.cos(tello.story[i, 3])
        ax.quiver(tello.story[i, 0], tello.story[i, 1], tello.story[i, 2],
                  c, s, 0,
                  length=10, normalize=True, color="black")
        ax.plot(
            tello.story[0:i+1, 0],
            tello.story[0:i+1, 1],
            tello.story[0:i+1, 2],
            c="red"
        )
        plt.pause(0.5)


