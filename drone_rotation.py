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

import platform
input_idx = 0
capture_api = None
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW

drone = None
drone, drone_edit_frame = DroneFactory.create(DroneFactory.DJITello, input_idx=input_idx, capture_api=capture_api)
drone_edit_frame.end()


x_orientation = 0
state = True

gyroscope_sample_rate = 119

def UpdateOrientation(drone):
    global x_orientation, state

    while state:
        time.sleep(0.5)
        if drone is None:
            x_orientation = x_orientation + 30 #np.random.randint(low=-180, high=180)
        else:
            x_orientation = -drone.yaw

# run the thread to update the x orientation in real time
t = Thread(target=UpdateOrientation, args=(drone,))
t.start()


try:
    while True:
        fig = plt.figure()

        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(0, 0, s=100, c='b')

        distance = 0.1
        x_orientation_rad = math.radians(x_orientation)
        x_pos = math.cos(x_orientation_rad)*distance
        y_pos = math.sin(x_orientation_rad)*distance

        ax.quiver(0, 0, 0, x_pos, y_pos, 0,
                  length=distance, normalize=True)

        ax.set_xlim(-distance, distance)
        ax.set_ylim(-distance, distance)
        ax.set_zlim(-distance, distance)

        fig.canvas.draw()
        plt.show()
        plt.pause(0.1)
except KeyboardInterrupt:
    pass
finally:
    state = False
    cv2.destroyAllWindows()
    if drone is not None:
        drone.end()
    t.join()


