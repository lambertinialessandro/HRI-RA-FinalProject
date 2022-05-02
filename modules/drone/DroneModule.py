from abc import ABC, abstractmethod
import cv2  # TODO: remove this and FakeDrone
import numpy as np

from djitellopy import Tello


class AbstractDrone(ABC):
    # Camera
    @property
    @abstractmethod
    def frame(self):
        pass

    # State
    @property
    @abstractmethod
    def battery(self) -> int:
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @property
    @abstractmethod
    def is_flying(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_streaming(self) -> bool:
        pass

    # Controls
    @abstractmethod
    def streamon(self):
        pass

    @abstractmethod
    def streamoff(self):
        pass

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


class DJITello(AbstractDrone):
    def __init__(self, host=None):
        super(DJITello, self).__init__()
        if host:
            self._tello = Tello(host)
        else:
            self._tello = Tello()
        self._tello.connect()

    @property
    def frame(self):
        return self._tello.get_frame_read().frame

    @property
    def battery(self) -> int:
        return self._tello.get_battery()

    @property
    def temperature(self) -> float:
        return self._tello.get_temperature()

    @property
    def height(self) -> int:
        return self._tello.get_height()

    @property
    def is_flying(self) -> bool:
        return self._tello.is_flying

    @property
    def is_streaming(self) -> bool:
        return self._tello.stream_on

    def streamon(self):
        if not self.is_streaming:
            self._tello.streamon()

    def streamoff(self):
        if self.is_streaming:
            self._tello.streamoff()

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


class FakeDrone(AbstractDrone):
    _stream_on = False
    _is_flying = False

    def __init__(self, capture_api=None):
        super(AbstractDrone, self).__init__()
        self.inputIdx = 0
        self.capture_api = capture_api
        self.w = 1280//2
        self.h = 720//2
        self.cap = None

    @property
    def frame(self):
        _, frame = self.cap.read()
        return frame

    @property
    def battery(self) -> int:
        return np.random.randint(low=1, high=101)

    @property
    def temperature(self) -> float:
        return np.random.randint(low=-40, high=40)

    @property
    def height(self) -> int:
        return np.random.randint(low=1, high=10)

    @property
    def is_streaming(self) -> bool:
        return self._stream_on

    @property
    def is_flying(self) -> bool:
        return self._is_flying

    def streamon(self):
        if not self._stream_on:
            self._stream_on = True
            self.cap = cv2.VideoCapture(self.inputIdx, self.capture_api)
            print("DRONE: Stream on")

    def streamoff(self):
        if self._stream_on:
            self._stream_on = False
            self.cap.release()
            cv2.destroyAllWindows()
            print("DRONE: Stream off")

    def set_rc_controls(self, lr, fb, up, j):
        pass

    def take_off(self):
        if not self._is_flying:
            self._is_flying = True
            print("DRONE: Take off")

    def land(self):
        if self._is_flying:
            self._is_flying = False
            print("DRONE: Land")

    def move_up(self, value):
        pass

    def move_down(self, value):
        pass

    def rotate_cw(self, value):
        pass

    def rotate_ccw(self, value):
        pass

    def end(self):
        if self._stream_on:
            self.cap.release()
