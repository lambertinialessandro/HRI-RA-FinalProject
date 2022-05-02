# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 19:39:26 2022

@author: lambe
"""

import cv2
import math
import time

import keyboard
import schedule

import matplotlib.pyplot as plt

from djitellopy import Tello


stereo = cv2.StereoBM_create(numDisparities=16, blockSize=5)
tello = Tello()
tello.connect()

tello.streamon()
frame_read = tello.get_frame_read()


'''
      A--------B
    H            C
    |            |
    |            |
    |            |
    G            D
      F--------E
'''

t_move = 3
t_img = 2

disp = 20
angle = 90

frame_read.frame
#while

try:
    tello.takeoff()
    time.sleep(t_img)
    A = frame_read.frame
    time.sleep(t_move)

    tello.move_right(disp)
    time.sleep(t_img)
    B = frame_read.frame
    time.sleep(t_move)

    tello.rotate_clockwise(angle)
    time.sleep(t_img)
    C = frame_read.frame
    time.sleep(t_move)

    tello.move_right(disp)
    time.sleep(t_img)
    D = frame_read.frame
    time.sleep(t_move)

    tello.rotate_clockwise(angle)
    time.sleep(t_img)
    E = frame_read.frame
    time.sleep(t_move)

    tello.move_right(disp)
    time.sleep(t_img)
    F = frame_read.frame
    time.sleep(t_move)

    tello.rotate_clockwise(angle)
    time.sleep(t_img)
    G = frame_read.frame
    time.sleep(t_move)

    tello.move_right(disp)
    time.sleep(t_img)
    H = frame_read.frame
    time.sleep(t_move)

    tello.rotate_clockwise(angle)
finally:
        tello.end()



f, ax = plt.subplots(nrows=1, ncols=3, figsize=(5, 5), dpi=80)
plt.setp(ax, xticks=[], yticks=[])
ax[0].imshow(A)
ax[1].imshow(B)
ax[2].imshow(stereo.compute(
    cv2.cvtColor(A, cv2.COLOR_BGR2GRAY),
    cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)), 'gray')
plt.show()

f, ax = plt.subplots(nrows=1, ncols=3, figsize=(5, 5), dpi=80)
plt.setp(ax, xticks=[], yticks=[])
ax[0].imshow(C)
ax[1].imshow(D)
ax[2].imshow(stereo.compute(
    cv2.cvtColor(C, cv2.COLOR_BGR2GRAY),
    cv2.cvtColor(D, cv2.COLOR_BGR2GRAY)), 'gray')
plt.show()

f, ax = plt.subplots(nrows=1, ncols=3, figsize=(5, 5), dpi=80)
plt.setp(ax, xticks=[], yticks=[])
ax[0].imshow(E)
ax[1].imshow(F)
ax[2].imshow(stereo.compute(
    cv2.cvtColor(E, cv2.COLOR_BGR2GRAY),
    cv2.cvtColor(F, cv2.COLOR_BGR2GRAY)), 'gray')
plt.show()

f, ax = plt.subplots(nrows=1, ncols=3, figsize=(5, 5), dpi=80)
plt.setp(ax, xticks=[], yticks=[])
ax[0].imshow(G)
ax[1].imshow(H)
ax[2].imshow(stereo.compute(
    cv2.cvtColor(G, cv2.COLOR_BGR2GRAY),
    cv2.cvtColor(H, cv2.COLOR_BGR2GRAY)), 'gray')
plt.show()


