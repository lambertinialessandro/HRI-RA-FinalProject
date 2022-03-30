from abc import ABC, abstractmethod

from djitellopy import Tello


class Drone(ABC):
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

    def end(self):
        self.end()
