# -*- coding: utf-8 -*-
"""
Created on Sat May  7 11:29:06 2022

@author: lambe
"""

from threading import Thread
import cv2
import time
import math
import numpy as np
from PIL import Image
import random

import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt

from modules.drone.DroneFactory import DroneFactory

# import platform
# input_idx = 0
# capture_api = None
# if platform.system() == 'Windows':
#     input_idx = 1
#     capture_api = cv2.CAP_DSHOW

# drone = None
# drone, drone_edit_frame = DroneFactory.create(DroneFactory.DJITello, input_idx=input_idx, capture_api=capture_api)
# drone_edit_frame.end()


# x_orientation = 0
# state = True

# gyroscope_sample_rate = 119

# def UpdateOrientation(drone):
#     global x_orientation, state

#     while state:
#         time.sleep(0.5)
#         if drone is None:
#             x_orientation = x_orientation + 30 #np.random.randint(low=-180, high=180)
#         else:
#             x_orientation = -drone.yaw

# # run the thread to update the x orientation in real time
# t = Thread(target=UpdateOrientation, args=(drone,))
# t.start()


# try:
#     while True:
#         fig = plt.figure()

#         ax = fig.add_subplot(111, projection='3d')
#         ax.scatter(0, 0, s=100, c='b')

#         distance = 0.1
#         x_orientation_rad = math.radians(x_orientation)
#         x_pos = math.cos(x_orientation_rad)*distance
#         y_pos = math.sin(x_orientation_rad)*distance

#         ax.quiver(0, 0, 0, x_pos, y_pos, 0,
#                   length=distance, normalize=True)

#         ax.set_xlim(-distance, distance)
#         ax.set_ylim(-distance, distance)
#         ax.set_zlim(-distance, distance)

#         fig.canvas.draw()
#         plt.show()
#         plt.pause(0.1)
# except KeyboardInterrupt:
#     pass
# finally:
#     state = False
#     cv2.destroyAllWindows()
#     if drone is not None:
#         drone.end()
#     t.join()






color = cv2.cvtColor(cv2.imread("color.jpeg", 3), cv2.COLOR_BGR2RGB)
# plt.imshow(color)
# plt.show()

depth = cv2.cvtColor(cv2.imread("depth.png"), cv2.COLOR_BGR2GRAY)
# plt.imshow(depth)
# plt.show()


def get_rotation_matrix(orientation, axis):
    c = math.cos(orientation)
    s = math.sin(orientation)

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

def plot_arrow_text(ax, px, py, pz, dx, dy, dz, dist,
                    txt, color, size):
    ax.quiver(px, py, pz, dx, dy, dz,
              length=dist, normalize=True, color=color)
    ax.text(px + dx * dist, py + dy * dist,pz + dz * dist,
            txt, color=color, size=size)

def plot_referential(ax, dist, x_orientation=None):
    if x_orientation is not None:
        origin = -dist, -dist, -dist
        ax.scatter(*origin, s=100, c='black')
        plot_arrow_text(ax, *origin, 1, 0, 0, dist/2, 'x', 'b', 15)
        plot_arrow_text(ax, *origin, 0, 1, 0, dist/2, 'y', 'r', 15)
        plot_arrow_text(ax, *origin, 0, 0, 1, dist/2, 'z', 'g', 15)

        origin = 0, 0, 0
        angle = math.radians(x_orientation)
        direction = math.cos(angle), math.sin(angle), 0
        plot_arrow_text(ax, *origin, *direction, dist, x_orientation, 'r', 15)
    else:
        origin = 0, 0, 0
        ax.scatter(*origin, s=100, c='black')
        plot_arrow_text(ax, *origin, 1, 0, 0, dist/2, 'x', 'b', 15)
        plot_arrow_text(ax, *origin, 0, 1, 0, dist/2, 'y', 'r', 15)
        plot_arrow_text(ax, *origin, 0, 0, 1, dist/2, 'z', 'g', 15)

    ax.set_xlim([-dist, dist])
    ax.set_ylim([-dist, dist])
    ax.set_zlim([-dist, dist])

def plot_3d_scene(fig, points_in_3d, depth_values):
    """
    Function plot a 3D scene from points and depth values
    Args:
        - (matplotlib figure) fig
        - (np.array) points_in_3d to display in the 3D env
        - (list) depth_values to calculate cmap and boundaries
    """
    ax = fig.add_subplot(111, projection='3d')

    # get colormap
    max_projection_value = max(depth_values)
    depth_values_normalized = depth_values/max_projection_value
    colormap = get_cmap(depth_values_normalized)

    # plot referential x, y, z
    plot_referential(ax, max_projection_value)

    # plot 3D projected points in simulation referential (-z, y, x)
    points_in_3d = points_in_3d.reshape([-1, 3])
    ax.scatter(-points_in_3d[:, 2], points_in_3d[:, 1],
               points_in_3d[:, 0], c=colormap, s=5)

    plt.show()
    plt.pause(0.5)





def plot_3d_points(ax, points_in_3d, depth_values,
                   max_projection_value):
    """
    Function to plot 3d points in environment with a colormap from get_cmap()
    Args:
        - (matplotlib ax3D) ax to plot arrows
        - (np.array) points_in_3d to display in the 3D env
        - (list) depth_values to calculate cmap and boundaries
        - (float) max_projection_value max depth values
    Return:
        - (bool) isLeft true if left, false if right
        - (float) value for the rescale
    """
    # get colormap
    depth_values_normalized = depth_values/max_projection_value
    colormap = get_cmap(depth_values_normalized)

    # plot 3D projected points in simulation referential (-z, y, x)
    points_in_3d = points_in_3d.reshape([-1, 3])
    ax.scatter(-points_in_3d[:, 2], points_in_3d[:, 1],
               points_in_3d[:, 0], c=colormap, s=5)

def plot_2d_top_view_referential(ax, dist, x_orientation = None,
                                 orientations_todo = [], orientations_done = []):
    origin = 0, 0, 0

    ax.scatter(*origin, s=100, c='b')

    for orientation in orientations_todo:
        angle = math.radians(orientation)
        direction = math.cos(angle), math.sin(angle), 0
        plot_arrow_text(ax, *origin, *direction, dist, orientation, 'r', 15)

    for orientation in orientations_done:
        angle = math.radians(orientation)
        direction = math.cos(angle), math.sin(angle), 0
        plot_arrow_text(ax, *origin, *direction, dist, orientation, 'g', 15)

    if x_orientation is not None:
        angle = math.radians(x_orientation)
        direction = math.cos(angle), math.sin(angle), 0
        plot_arrow_text(ax, *origin, *direction, dist, 'robot', 'black', 15)

    ax.set_xlim([-dist, dist])
    ax.set_ylim([-dist, dist])
    ax.set_zlim([-dist, dist])

def overlap_img_with_segmap(img, module_output):
    """
    Function to overlap segmentation map with image
    Args:
        - (cv2.image) Raw input image in RGB
        - (numpy array) module_output : output of the model
    Return:
        - (numpy array) overlap between img and module_output
    """
    origin_height, origin_width, _ = img.shape
    im_pil = Image.fromarray(img)

    depth_min = module_output.min()
    depth_max = module_output.max()

    # rescale depthmap between 0-255
    depth_rescaled = (255 * (module_output - depth_min) /
                      (depth_max - depth_min)).astype("uint8")
    depth_rescaled_3chn = cv2.cvtColor(depth_rescaled,
                                       cv2.COLOR_GRAY2RGB)
    module_output_3chn = cv2.applyColorMap(depth_rescaled_3chn,
                                           cv2.COLORMAP_RAINBOW)
    module_output_3chn = cv2.resize(module_output_3chn,
                                    (origin_width, origin_height),
                                    interpolation=cv2.INTER_CUBIC)
    seg_pil = Image.fromarray(module_output_3chn.astype('uint8'), 'RGB')

    overlap = Image.blend(im_pil, seg_pil, alpha=0.6)

    return np.array(overlap), module_output_3chn

def crop_depth_map(depth_map, margin_percentage):
    """
    Crop margins on input depth_map
    Args:
        - (numpy array) format [width, height, channel]
        - (float) percentage [0: 100]
    Return:
        - (numpy array) format [width-2*margin, height-2*margin, channel]
    """
    width, height = depth_map.shape
    margin_from_0_to_1 = margin_percentage/100

    first_width_idx = int(width * margin_from_0_to_1)
    first_height_idx = int(height * margin_from_0_to_1)

    last_width_idx = int(width * (1-margin_from_0_to_1))
    last_height_idx = int(height * (1-margin_from_0_to_1))

    return depth_map[first_width_idx:last_width_idx,
                     first_height_idx:last_height_idx]

def rescale_depth_map(depth_map, min_dist, max_dist):
    """
    Rescale depth map from min_dist to max_dist
    Args:
        - (numpy array) format [width, height, channel]
        - (float) percentage [0: 100]
    Return:
        - (float) min_dist to rescale the generated depth map
        - (float) max_dist to rescale the generated depth map
            depth=depth/depth.max*(max_dist-min_dist)+min_dist
    """
    depth_max = depth_map.max()
    total_range = max_dist - min_dist
    rescaled_depth_map = depth_map / depth_max * total_range + min_dist

    return rescaled_depth_map

def get_closest_corner(orientation, corners_distance):
    """
    Function to call to know which corner to rescale for a given orientation
    And the value to use
    Args:
        - (float) current orientation for a depth map to rescale
        - (dict of tuples 2 values) format orientation: (top left, top right)
    Return:
        - (bool) is_left true if left, false if right
        - (float) value for the rescale
    """
    is_left = True

    closest_orientation = min(corners_distance.keys(),
                              key=lambda x: abs(x-orientation))

    if closest_orientation < orientation:
        is_left = False

    return is_left, corners_distance[closest_orientation][is_left]


def get_3d_points_from_depthmap(points_in_3d, depth_values,
                                depth_map, x_orientation,
                                per_mil_to_keep=1):
    IMAGE_WIDTH = 256
    IMAGE_HEIGHT = 256

    H_FOV_DEGREES = 60
    H_FOV_RAD = math.radians(H_FOV_DEGREES)
    V_FOV_RAD = math.radians(IMAGE_HEIGHT/IMAGE_WIDTH*H_FOV_DEGREES)
    X_FOCAL = IMAGE_WIDTH / (2*math.tan(H_FOV_RAD/2))
    Y_FOCAL = IMAGE_HEIGHT / (2*math.tan(V_FOV_RAD/2))
    X_CENTER_COORDINATE = (0.5*IMAGE_WIDTH)
    Y_CENTER_COORDINATE = (0.5*IMAGE_HEIGHT)

    depth_width, depth_height = depth_map.shape
    x_depth_rescale_factor = depth_width / IMAGE_WIDTH
    y_depth_rescale_factor = depth_height / IMAGE_HEIGHT

    for x in range(IMAGE_WIDTH):
        for y in range(IMAGE_HEIGHT):

            # keep n per-mil points
            if random.randint(0, 999) >= per_mil_to_keep:
                continue

            x_depth_pos = int(x*x_depth_rescale_factor)
            y_depth_pos = int(y*y_depth_rescale_factor)
            depth_value = depth_map[x_depth_pos, y_depth_pos]

            # get 3d vector
            x_point = depth_value * (x - X_CENTER_COORDINATE) / X_FOCAL
            y_point = depth_value * (y - Y_CENTER_COORDINATE) / Y_FOCAL
            point_3d_before_rotation = np.array([x_point, y_point,
                                                 depth_value])

            # projection in function of the orientation
            point_3d_after_rotation = np.matmul(
                get_rotation_matrix(math.radians(x_orientation), axis="x"),
                point_3d_before_rotation)
            points_in_3d = np.append(points_in_3d, point_3d_after_rotation)
            depth_values.append(depth_value)
    return points_in_3d, depth_values

def plot_env(fig, x_orientation, points_in_3d, depth_values, rgb_img,
             orientations_done, orientations_todo,
             depth_map, images, depth_maps, overlaps_img_depth,
             corners_distance, max_projection_value=2., per_mil_to_keep=1,
             offset_ok=2.5, project_depth=True, percentage_margin_on_depth=0):
    """
    Project depth values into 3D point according to the robot orientation
    Uses global variable x_orientation
    Args:
        - (matplotlib.figure) fig to plot environment
        - (float) x_orientation of the robot
        - (np.array) points_in_3d to display in the 3D env
        - (list) depth_values to calculate cmap and boundaries
        - (cv2 image) image in rgb format
        - (tf.lite.Interpreter) tflite interpreter
        - (list) orientations_done list of orientations already projected
        - (list) orientations_todo list of orientations to project
        - (cv2 image) depth_map format (width, height, 1)
        - (dict of orientation: numpy.array) images used for projections
        - (dict of orientation: numpy.array) depth_maps used for projections
        - (dict of orientation: numpy.array) overlap between img and depth_map
        - (dict of tuples 2 values) format orientation: (top left, top right)
        - (float) max_projection_value max depth value
        - (int) per_mil_to_keep: per-mil of depth points to project
        - (float) offset to accept the current orientation of the robot to do
            and angle in orientations_todo
        - (boolean) project_depth enables depth calculation and projection
        - (float) margin percentage to remove from the depth [0: 100]
    """
    plt.gcf().clear()

    fig = plt.figure()

    ax = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(224)

    # hide grid
    ax2.grid(False)
    ax3.grid(False)

    # hide ticks
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax3.set_xticks([])
    ax3.set_yticks([])

    if len(points_in_3d) > 0:
        max_projection_value = max(depth_values)
        plot_3d_points(ax, points_in_3d, depth_values,
                       max_projection_value)

    plot_referential(ax, max_projection_value, x_orientation=x_orientation)

    plot_2d_top_view_referential(ax3, 0.1, x_orientation,
                                 orientations_todo, orientations_done)

    if project_depth:
        for i, orientation in enumerate(orientations_todo):
            if orientation - offset_ok <= x_orientation\
                    <= orientation + offset_ok:

                fig = plt.figure()

                ax = fig.add_subplot(121, projection='3d')
                ax2 = fig.add_subplot(222)
                ax3 = fig.add_subplot(224)

                # hide grid
                ax2.grid(False)
                ax3.grid(False)

                # hide ticks
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax3.set_xticks([])
                ax3.set_yticks([])

                # get 3d points in real referential
                # depth_map = depth_manager.run_tflite_interpreter(rgb_img,
                #                                                  interpreter)
                overlap, depth_map_3chn = \
                    overlap_img_with_segmap(rgb_img, depth_map)
                images[orientation] = np.asarray(rgb_img, dtype="uint8")
                depth_maps[orientation] = depth_map_3chn
                overlaps_img_depth[orientation] = overlap

                ax2.imshow(overlap)
                plt.show()
                plt.pause(0.2)

                depth_map = crop_depth_map(
                    depth_map, percentage_margin_on_depth)

                # TODO
                min_dist = 0# float(input("Min distance: "))
                max_dist = 500# float(input("Max distance: "))

                depth_map = rescale_depth_map(
                    depth_map, min_dist, max_dist)

                if len(orientations_done) == 0:
                    corners_distance[orientation] = [depth_map[0, 0], depth_map[0, -1]]
                else:
                    is_left, corner_value = get_closest_corner(orientation, corners_distance)
                    depth_map = depth_map / depth_map[0, -int(not is_left)] * corner_value
                    corners_distance[orientation] = [depth_map[0, 0], depth_map[0, -1]]

                points_in_3d, depth_values = \
                    get_3d_points_from_depthmap(points_in_3d, depth_values,
                                                depth_map, x_orientation,
                                                per_mil_to_keep)
                orientations_done.append(orientation)
                del orientations_todo[i]
                break

    ax2.imshow(rgb_img)

    plt.show()
    plt.pause(0.2)

    return depth_map, points_in_3d, depth_values,\
        images, depth_maps, overlaps_img_depth





fig_simulation = plt.figure()
X_ORIENTATION = 0
points_in_3d = np.array([])
depth_values = []

orientations_done = []
orientations_todo = [orientation for orientation
                     in range(0, 359, 30)]

images = {}
depth_maps = {}
overlaps_img_depth = {}
corners_distance = {}



depth_map, points_in_3d, depth_values,\
images, depth_maps, overlaps = \
            plot_env(
                fig_simulation, X_ORIENTATION, points_in_3d,
                depth_values, color,
                orientations_done, orientations_todo, depth,
                images, depth_maps, overlaps_img_depth,
                corners_distance,
                per_mil_to_keep=1,
                percentage_margin_on_depth=2)

# stop if all todo orientations were done
if not orientations_todo:

    plt.gcf().clear()
    matplotlib.interactive(False)
    plot_3d_scene(fig_simulation, points_in_3d, depth_values)



