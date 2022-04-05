
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.drone.DroneModule import DJITello, FakeDrone


class DroneFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    def __init__(self):
        pass

    @staticmethod
    def create(type_drone, capture_api=None):
        drone = None
        if type_drone == DroneFactory.DJITello:
            drone = DJITello()
        elif type_drone == DroneFactory.FakeDrone:
            drone = FakeDrone(capture_api=capture_api)

        return drone


# TODO
# only for debug, to be deleted
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


