#!/usr/local/bin/python3

import cv2

from modules.drone.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


import platform
capture_api = None

if platform.system() == 'Windows':
    capture_api = cv2.CAP_DSHOW


# BUILDING THE DRONE
drone = DroneFactory.create(DroneFactory.DJITello, capture_api=capture_api) # capture_api to be deleted

# BUILDING EXECUTION SEQUENCE
template_pattern = GlobalFactory.create(GlobalFactory.VideoDrone, drone=drone, capture_api=capture_api)


# STARTING THE EXECUTION SEQUENCE
template_pattern.execute()


#
# for debugging schedule.get_jobs()
#


