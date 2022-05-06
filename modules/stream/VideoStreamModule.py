from abc import ABC, abstractmethod
import cv2
import numpy as np

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
        frame = self.drone.frame
        if frame is not None:
            frame = cv2.resize(self.drone.frame, (self.w, self.h))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame = np.zeros((self.h, self.w, 3), np.uint8)
        return frame

    def end(self):
        self.drone.streamoff()


class WebcamStream(AbstractVideoStream):
    def __init__(self, input_idx=0, capture_api=None):
        super().__init__()

        self.input_idx = input_idx
        self.w = 1280//2
        self.h = 720//2

        self.cap = cv2.VideoCapture(self.input_idx, capture_api)

    def get_stream_frame(self):
        _, frame = self.cap.read()
        frame = cv2.resize(frame, (self.w, self.h))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def end(self):
        self.cap.release()


