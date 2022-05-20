# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:27:56 2022

@author: lambe
"""

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

img = np.array([[1000, 0], [0, 1000]])
print(img)
plt.imshow(img)
plt.show()

# print(1/img)
# plt.imshow(1/img)

max_v = img.max()

print(max_v-img)
plt.imshow(max_v-img)
plt.show()

