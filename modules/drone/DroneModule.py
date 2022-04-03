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

    @property
    @abstractmethod
    def is_flying(self):
        pass

    @property
    @abstractmethod
    def is_streaming(self):
        pass

    # Controls
    @abstractmethod
    def set_rc_controls(self, lr, fb, up, j):
        pass

    @abstractmethod
    def take_off(self):
        pass

    @abstractmethod
    def land(self):
        pass

    @abstractmethod
    def move_up(self, value):
        pass

    @abstractmethod
    def move_down(self, value):
        pass

    @abstractmethod
    def rotate_cw(self, value):
        pass

    @abstractmethod
    def rotate_ccw(self, value):
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
        if not self.is_streaming:
            self._tello.streamon()

    def streamoff(self):
        if self.is_streaming:
            self._tello.streamoff()

    @property
    def battery(self):
        return self._tello.get_battery()

    @property
    def is_flying(self):
        return self._tello.is_flying

    @property
    def is_streaming(self):
        return self._tello.stream_on

    def set_rc_controls(self, lr, fb, up, j):
        return self._tello.send_rc_control(lr, fb, up, j)

    def take_off(self):
        if not self.is_flying:
            self._tello.takeoff()

    def land(self):
        # if self.is_flying:
        self._tello.land()

    def move_up(self, value):
        self._tello.move_up(value)

    def move_down(self, value):
        self._tello.move_down(value)

    def rotate_cw(self, value):
        self._tello.rotate_clockwise(value)

    def rotate_ccw(self, value):
        self._tello.rotate_counter_clockwise(value)

    def end(self):
        self._tello.end()


class FakeDrone(Drone):
    _stream_on = False
    _is_flying = False

    def __init__(self, capture_api=None):
        super(Drone, self).__init__()
        self.inputIdx = 0
        self.capture_api = capture_api
        self.w = 1280//2
        self.h = 720//2
        self.cap = None

    @property
    def frame(self):
        _, frame = self.cap.read()
        return frame

    def streamon(self):
        if not self._stream_on:
            self._stream_on = True
            self.cap = cv2.VideoCapture(self.inputIdx, self.capture_api)
            print("Stream on")

    def streamoff(self):
        if self._stream_on:
            self._stream_on = False
            self.cap.release()
            cv2.destroyAllWindows()
            print("Stream off")

    @property
    def battery(self):
        return str(np.random.randint(low=1, high=101))

    @property
    def is_streaming(self):
        return self._stream_on

    @property
    def is_flying(self):
        return self._is_flying

    def set_rc_controls(self, lr, fb, up, j):
        pass

    def take_off(self):
        if not self._is_flying:
            self._is_flying = True
            print("Take off")

    def land(self):
        if self._is_flying:
            self._is_flying = False
            print("Land")

    def rotate_cw(self, value):
        pass

    def rotate_ccw(self, value):
        pass

    def end(self):
        if self.is_streaming:
            self.cap.release()
        cv2.destroyAllWindows()
