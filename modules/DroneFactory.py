# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:20:52 2022

@author: lambe
"""

import sys
sys.path.append('../')

from modules.drone.DroneModule import DJITello, FakeDrone


class DroneFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    def __init__(self):
        pass

    @staticmethod
    def create(capture_api=None):
        drone = None

        print("Which Drone? \n"+
              "    1) DJITello \n"+
              "    2) FakeDrone \n")
        type_drone = input('Drone: ')

        if type_drone == "1":  # DJITello
            drone = DJITello()
        elif type_drone == "2":  # FakeDrone
            drone = FakeDrone(capture_api=capture_api)

        return drone


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == 'Windows':
        capture_api = cv2.CAP_DSHOW

    drone = DroneFactory.create(capture_api=capture_api)
    drone.streamon()

    try:
        while True:
            img = drone.frame
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        drone.streamoff()
        drone.end()