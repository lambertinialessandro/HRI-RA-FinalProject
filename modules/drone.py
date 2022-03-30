from abc import ABC, abstractmethod

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

    def take_off(self):
        self._tello.takeoff()

    def land(self):
        self._tello.land()

    def end(self):
        self.end()
