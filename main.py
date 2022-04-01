#!/usr/local/bin/python3

import cv2

from modules.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


import platform
capture_api = None
if platform.system() == 'Windows':
    capture_api = cv2.CAP_DSHOW


# BUILDING THE DRONE
df = DroneFactory()
drone = df.create(capture_api=capture_api)

# BUILDING EXECUTION SEQUENCE
gf = GlobalFactory()
templatye_pattern = gf.create(drone=drone, capture_api=capture_api)


# STARTING THE EXECUTION SEQUENCE
templatye_pattern.execute()


#
# for debugging schedule.get_jobs()
#


