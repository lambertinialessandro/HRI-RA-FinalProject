
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.drone.DroneModule import DJITello, FakeDrone
from modules.drone.DroneEditFrame import DroneEditFrame


class DroneFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    def __init__(self):
        pass

    @staticmethod
    def create(type_drone, input_idx=0, capture_api=None):
        drone = None
        drone_edit_frame = None
        if type_drone == DroneFactory.DJITello:
            drone = DJITello()
            drone_edit_frame = DroneEditFrame(drone)
        elif type_drone == DroneFactory.FakeDrone:
            drone = FakeDrone(input_idx=input_idx, capture_api=capture_api)
            drone_edit_frame = DroneEditFrame(drone)

        return drone, drone_edit_frame


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == 'Windows':
        capture_api = cv2.CAP_DSHOW

    drone = DroneFactory.create(DroneFactory.DJITello, capture_api=capture_api)
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
