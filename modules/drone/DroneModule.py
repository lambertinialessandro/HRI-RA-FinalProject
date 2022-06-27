import time
from abc import ABC, abstractmethod

import math
import cv2  # TODO: remove this and FakeDrone
import numpy as np
from threading import Thread

from djitellopy import Tello


class AbstractDrone(ABC):
    def __init__(self):
        self.curr_pos = [0.0, 0.0, 0.0]
        self.curr_ang = 0.0

        self._queue = []

        self.__thread = Thread(target=self.__perform_command)
        self.__thread.start()

    def __perform_command(self):
        while self._queue is not None:
            try:
                command = self._queue.pop(0)
                if len(command) > 1:
                    command[0](*command[1])
                else:
                    command[0]()
                time.sleep(0.05)
            except IndexError:
                pass

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
    def wifi_snr(self) -> int:
        pass

    @property
    @abstractmethod
    def yaw(self) -> float:
        pass

    @property
    @abstractmethod
    def is_flying(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_streaming(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_cooling(self) -> bool:
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
    def move_forward(self, value):
        pass

    @abstractmethod
    def move_backward(self, value):
        pass

    @abstractmethod
    def move_left(self, value):
        pass

    @abstractmethod
    def move_right(self, value):
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
    def turn_motor_on(self):
        pass

    @abstractmethod
    def turn_motor_off(self):
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

        self._is_cooling = False

    @property
    def frame(self):
        return self._tello.get_frame_read().frame

    @property
    def battery(self) -> int:
        """range 0 - 100"""
        return self._tello.get_battery()

    @property
    def temperature(self) -> float:
        return self._tello.get_temperature()

    @property
    def height(self) -> int:
        return self._tello.get_height()

    @property
    def wifi_snr(self) -> str:
        return self._tello.query_wifi_signal_noise_ratio()

    @property
    def yaw(self) -> int:
        """range -180 - 180"""
        return self._tello.get_yaw()

    @property
    def is_flying(self) -> bool:
        return self._tello.is_flying

    @property
    def is_streaming(self) -> bool:
        return self._tello.stream_on

    @property
    def is_cooling(self) -> bool:
        return self._is_cooling

    def streamon(self):
        if not self.is_streaming:
            self._tello.streamon()

    def streamoff(self):
        if self.is_streaming:
            self._tello.streamoff()

    def set_rc_controls(self, lr, fb, up, j):
        self._queue.append([self._tello.send_rc_control, (lr, fb, up, j)])

    def take_off(self):
        if not self.is_flying:
            self._queue.append([self._tello.takeoff])

    def land(self):
        # if self.is_flying:
        self._queue.append([self._tello.land])

    def move_forward(self, value):
        self._queue.append([self._tello.move_forward, [value]])

    def move_backward(self, value):
        self._queue.append([self._tello.move_back, [value]])

    def move_left(self, value):
        self._queue.append([self._tello.move_left, [value]])

    def move_right(self, value):
        self._queue.append([self._tello.move_right, [value]])

    def move_up(self, value):
        self._queue.append([self._tello.move_up, [value]])

    def move_down(self, value):
        self._queue.append([self._tello.move_down, [value]])

    def rotate_cw(self, value):
        self._queue.append([self._tello.rotate_clockwise, [value]])

    def rotate_ccw(self, value):
        self._queue.append([self._tello.rotate_counter_clockwise, [value]])

    def turn_motor_on(self):
        self._queue.append([self._tello.turn_motor_on])

    def turn_motor_off(self):
        self._tello.turn_motor_off()

    def end(self):
        self._queue = None
        self._tello.end()


class FakeDrone(AbstractDrone):
    _stream_on = False
    _is_flying = False

    def __init__(self, input_idx=0, capture_api=None):
        super(FakeDrone, self).__init__()
        self.inputIdx = input_idx
        self.capture_api = capture_api
        self.w = 1280//2
        self.h = 720//2
        self.cap = None

        self._is_cooling = False

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
    def wifi_snr(self) -> int:
        return np.random.randint(low=1, high=10)

    @property
    def yaw(self) -> int:
        return np.random.randint(low=-180, high=180)

    @property
    def is_streaming(self) -> bool:
        return self._stream_on

    @property
    def is_flying(self) -> bool:
        return self._is_flying

    @property
    def is_cooling(self) -> bool:
        return self._is_cooling

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

    def move_forward(self, value):
        self.curr_pos = [self.curr_pos[0] + value * math.cos(self.curr_ang),
                         self.curr_pos[1] + value * math.sin(self.curr_ang),
                         self.curr_pos[2]]

    def move_backward(self, value):
        self.curr_pos = [self.curr_pos[0] - value * math.cos(self.curr_ang),
                         self.curr_pos[1] - value * math.sin(self.curr_ang),
                         self.curr_pos[2]]

    def move_left(self, value):
        angle = self.curr_ang - math.pi / 2
        self.curr_pos = [self.curr_pos[0] + value * math.cos(angle),
                         self.curr_pos[1] + value * math.sin(angle),
                         self.curr_pos[2]]

    def move_right(self, value):
        angle = self.curr_ang + math.pi / 2
        self.curr_pos = [self.curr_pos[0] + value * math.cos(angle),
                         self.curr_pos[1] + value * math.sin(angle),
                         self.curr_pos[2]]

    def move_up(self, value):
        self.curr_pos = [self.curr_pos[0],
                         self.curr_pos[1],
                         self.curr_pos[2] + value]

    def move_down(self, value):
        self.curr_pos = [self.curr_pos[0],
                         self.curr_pos[1],
                         self.curr_pos[2] - value]

    def rotate_cw(self, value):
        angle = self.curr_ang + value * math.pi / 180
        self.curr_ang = self.curr_ang + math.radians(angle)

    def rotate_ccw(self, value):
        angle = self.curr_ang - value * math.pi / 180
        self.curr_ang = self.curr_ang + math.radians(angle)

    def turn_motor_on(self):
        pass

    def turn_motor_off(self):
        pass

    def end(self):
        if self._stream_on:
            self.cap.release()
