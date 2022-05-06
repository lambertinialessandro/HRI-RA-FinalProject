#!/usr/local/bin/python3

import cv2

#from modules.drone.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


import platform
input_idx = 0
capture_api = None
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW

import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
port = 9999


# 1. Drone is created
#drone, drone_edit_frame = DroneFactory.create(DroneFactory.FakeDrone, capture_api=capture_api)  # capture_api to be deleted

# FakeDrone  DJITello
# VideoDrone  VideoPC

# 2. Creating the sequence
template_pattern = GlobalFactory.create(GlobalFactory.DJITello, GlobalFactory.VideoDrone,
                                        input_idx=input_idx, capture_api=capture_api)

# 3. start web streaming
#template_pattern.start_web_streaming(ip, port)

# 4. Starting sequence
template_pattern.execute()

#
# for debugging:
#   import schedule
#   schedule.get_jobs()
#
