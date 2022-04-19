from abc import ABC, abstractmethod
import cv2

from modules.drone.DroneModule import AbstractDrone as Drone


class AbstractVideoStream(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_stream_frame(cls):
        pass

    @classmethod
    @abstractmethod
    def end(cls):
        pass


class VideoDroneStream(AbstractVideoStream):
    def __init__(self, drone: Drone):
        super().__init__()
        self.drone = drone
        self.w = 1280//2
        self.h = 720//2

        drone.streamon()

    def get_stream_frame(self):
        frame = cv2.resize(self.drone.frame, (self.w, self.h))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # TODO
        return frame

    def end(self):
        self.drone.streamoff()


class WebcamStream(AbstractVideoStream):
    def __init__(self, capture_api=None):
        super().__init__()

        self.inputIdx = 0
        self.w = 1280//2
        self.h = 720//2

        self.cap = cv2.VideoCapture(self.inputIdx, capture_api)

    def get_stream_frame(self):
        _, frame = self.cap.read()
        return frame

    def end(self):
        self.cap.release()


