# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:20:52 2022

@author: lambe
"""

import sys
sys.path.append('../')

import cv2

from modules.drone.DroneModule import DJITello, FakeDrone


class DroneFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    def __init__(self):
        pass

    def create(self, type_drone, CaptureAPI=None):
        drone = None
        if type_drone == self.DJITello:
            drone = DJITello()
        elif type_drone == self.FakeDrone:
            drone = FakeDrone(CaptureAPI=cv2.CAP_DSHOW)

        return drone


if __name__ == "__main__":
    import cv2

    df = DroneFactory()
    drone = df.create(DroneFactory.FakeDrone, CaptureAPI=cv2.CAP_DSHOW) # cv2.CAP_DSHOW, None
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