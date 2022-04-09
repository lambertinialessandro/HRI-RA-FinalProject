
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.drone.DroneModule import DJITello, FakeDrone
from modules.DrawerModule import PipelineDrawerBuilder

class DroneEditFrame():
    def __init__(self, drone):
        self.pd = PipelineDrawerBuilder.build(drone,
                                              [PipelineDrawerBuilder.DRAWER_FPS,
                                               PipelineDrawerBuilder.DRONE_BATTERY,
                                               PipelineDrawerBuilder.DRONE_TEMPERATURE,
                                               PipelineDrawerBuilder.DRONE_HEIGHT])

    def edit(self, frame):
        self.pd.draw(frame)

        return frame

    def end(self):
        pass

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
            drone_edit_frame = DroneEditFrame(drone)
        elif type_drone == DroneFactory.FakeDrone:
            drone = FakeDrone(capture_api=capture_api)
            drone_edit_frame = DroneEditFrame(drone)

        return drone, drone_edit_frame


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


