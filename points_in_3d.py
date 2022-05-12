# -*- coding: utf-8 -*-
"""
Created on Mon May  9 09:49:42 2022

@author: lambe
"""

import matplotlib.pyplot as plt
import math
import cv2
import random
import numpy as np
from matplotlib import cm


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

def plot_arrow_text(ax, px, py, pz, dx, dy, dz, dist,
                    txt, color, size):
    ax.quiver(px, py, pz, dx, dy, dz,
              length=dist, normalize=True, color=color)
    ax.text(px + dx * dist, py + dy * dist,pz + dz * dist,
            txt, color=color, size=size)

def get_cmap(values, cmap_name='rainbow'):
    cmap = cm.get_cmap(cmap_name, 12)
    depth_values_normalized = values/max(values)
    return cmap(depth_values_normalized)

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
    ax = fig.add_subplot(111, projection='3d')

    max_projection_value = max(depth_values)
    depth_values_normalized = depth_values/max_projection_value
    colormap = get_cmap(depth_values_normalized)

    # plot_referential(ax, 100) # TODO

    points_in_3d = points_in_3d.reshape([-1, 3])
    ax.scatter(-points_in_3d[:, 0], points_in_3d[:, 1], points_in_3d[:, 2],
                c=colormap, s=5)

    dist = 300 # TODO
    ax.set_xlim([-dist, dist])
    ax.set_ylim([-dist, dist])
    ax.set_zlim([-100, 100])

    plt.show()
    plt.pause(0.5)

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
            depth_value = depth_map[x_depth_pos, y_depth_pos] +50 # TODO

            # get 3d vector
            x_point = depth_value * (x - X_CENTER_COORDINATE) / X_FOCAL
            y_point = depth_value * (y - Y_CENTER_COORDINATE) / Y_FOCAL
            point_3d_before_rotation = np.array([x_point, y_point,
                                                 depth_value])

            # projection in function of the orientation
            point_3d_after_rotation = np.matmul(get_rotation_matrix(math.radians(90), axis="y"),
                                                np.matmul(
                get_rotation_matrix(math.radians(x_orientation), axis="x"),
                point_3d_before_rotation))
            points_in_3d = np.append(points_in_3d, point_3d_after_rotation)
            depth_values.append(depth_value)
    return points_in_3d, depth_values



############################################################# plot_arrow_text #
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# origin = 0, 0, 0
# dist = 0.09
# for i in range(0, 360, 45):
#     angle = math.radians(i)
#     direction = math.cos(angle), math.sin(angle), 0
#     plot_arrow_text(ax, *origin, *direction, dist, i, 'r', 15)
##########################################################



############################################################ plot_referential #
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# plot_referential(ax, 0.1, 0)
# plt.show()
##########################################################



################################################ plot_2d_top_view_referential #
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

step = 60
angle_done = 0
orientations_todo = [i for i in range(angle_done, 360, step)]
orientations_done = [i for i in range(0, angle_done, step)]

plot_2d_top_view_referential(ax, 0.1, None, orientations_todo, orientations_done)
plt.show()
##########################################################



################################# get_3d_points_from_depthmap # plot_3d_scene #
rgb_image = cv2.cvtColor(cv2.imread("rgb_image2.jpeg", 3), cv2.COLOR_BGR2RGB)
depth_image = cv2.cvtColor(cv2.imread("depth_image2.png"), cv2.COLOR_BGR2GRAY)
plt.imshow(rgb_image)
plt.show()
plt.imshow(depth_image)
plt.show()

points_in_3d = np.array([])
depth_values = []
x_orientation = 45*7

points_in_3d, depth_values = get_3d_points_from_depthmap(
                                    points_in_3d,
                                    depth_values,
                                    depth_image,
                                    x_orientation,
                                    per_mil_to_keep=50)

fig = plt.figure()
plot_3d_scene(fig, points_in_3d, depth_values)
##########################################################



########################################################### for plot_3d_scene #
rgb_image = cv2.cvtColor(cv2.imread("rgb_image2.jpeg", 3), cv2.COLOR_BGR2RGB)
depth_image = cv2.cvtColor(cv2.imread("depth_image2.png"), cv2.COLOR_BGR2GRAY)
plt.imshow(rgb_image)
plt.show()
plt.imshow(depth_image)
plt.show()

points_in_3d = np.array([])
depth_values = []

angle = 60
for i in range(360//angle):
    points_in_3d, depth_values = get_3d_points_from_depthmap(
                                        points_in_3d,
                                        depth_values,
                                        depth_image,
                                        angle*i,
                                        per_mil_to_keep=50)

fig = plt.figure()
plot_3d_scene(fig, points_in_3d, depth_values)
##########################################################



#########################################################  #

##########################################################



#########################################################  #

##########################################################



#########################################################  #

##########################################################



#########################################################  #

##########################################################



#########################################################  #

##########################################################



#########################################################  #

##########################################################








