#!/usr/local/bin/python3

import cv2
import schedule

from modules.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


import platform
capture_api = None
if platform.system() == 'Windows':
    capture_api = cv2.CAP_DSHOW


df = DroneFactory()
drone = df.create(capture_api=capture_api)

gf = GlobalFactory()
templatye_pattern = gf.create(drone=drone, capture_api=capture_api)


battery = drone.battery
schedule.every(10).seconds.do(lambda: globals().__setitem__("battery", drone.battery))


templatye_pattern.execute()






