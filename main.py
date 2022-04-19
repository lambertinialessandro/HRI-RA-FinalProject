#!/usr/local/bin/python3

import cv2

#from modules.drone.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


import platform
capture_api = None
if platform.system() == 'Windows':
    capture_api = cv2.CAP_DSHOW


# 1. Drone is created
#drone, drone_edit_frame = DroneFactory.create(DroneFactory.FakeDrone, capture_api=capture_api)  # capture_api to be deleted

# 2. Creating the sequence
template_pattern = GlobalFactory.create(GlobalFactory.FakeDrone, GlobalFactory.VideoDrone,
                                        capture_api=capture_api)

# 3. Starting sequence
template_pattern.execute()

#
# for debugging:
#   import schedule
#   schedule.get_jobs()
#
