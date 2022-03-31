
from abc import ABC, abstractmethod
import cv2
import numpy as np

from djitellopy import Tello


class Drone(ABC):
    # Camera
    @property
    @abstractmethod
    def frame(self):
        pass

    @abstractmethod
    def streamon(self):
        pass

    @abstractmethod
    def streamoff(self):
        pass

    # State
    @property
    @abstractmethod
    def battery(self):
        pass

    # Controls
    @abstractmethod
    def take_off(self):
        pass

    @abstractmethod
    def land(self):
        pass

    @abstractmethod
    def end(self):
        pass


class DJITello(Drone):
    def __init__(self):
        super(DJITello, self).__init__()
        self._tello = Tello()
        self._tello.connect()

    @property
    def frame(self):
        return self._tello.get_frame_read().frame

    def streamon(self):
        self._tello.streamon()

    def streamoff(self):
        self._tello.streamoff()

    @property
    def battery(self):
        return self._tello.get_battery()

    @property
    def is_flying(self):
        return self._tello.is_flying

    @property
    def stream_on(self):
        return self._tello.stream_on

    def take_off(self):
        self._tello.takeoff()

    def land(self):
        self._tello.land()

    def end(self):
        self._tello.end()


class FakeDrone(Drone):
    _stream_on = False
    _is_flying = False

    def __init__(self, CaptureAPI=None):
        super(Drone, self).__init__()
        self.inputIdx = 0
        self.CaptureAPI = CaptureAPI
        self.w = 1280//2
        self.h = 720//2

    @property
    def frame(self):
        _, frame = self.cap.read()
        return frame

    def streamon(self):
        self._stream_on = True
        self.cap = cv2.VideoCapture(self.inputIdx, self.CaptureAPI)
        print("Stream on")

    def streamoff(self):
        self._stream_on = False
        self.cap.release()
        cv2.destroyAllWindows()
        print("Stream off")

    @property
    def battery(self):
        return str(np.random.randint(low=1, high=101))

    @property
    def stream_on(self):
        return self._stream_on

    @property
    def is_flying(self):
        return self._is_flying

    def take_off(self):
        self._is_flying = True
        print("Take off")

    def land(self):
        self._is_flying = False
        print("Land")

    def end(self):
        if self.stream_on:
            self.cap.release()
        cv2.destroyAllWindows()


