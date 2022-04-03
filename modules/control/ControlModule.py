from abc import ABC
from enum import Enum
from threading import Thread

from modules.drone.DroneModule import Drone


class Command(Enum):
    TAKE_OFF = 1
    LAND = 2
    STREAM_ON = 3
    STREAM_OFF = 4

    MOVE_FORWARD = 10

    MOVE_BACKWARD = 20

    ROTATE_CW = 30

    ROTATE_CCW = 40

    FOLLOW_ME = 100

    STOP_EXECUTION = 1000

    def __str__(self):
        return self.name


class ControlModule(ABC):
    def __init__(self, drone: Drone):
        self._drone = drone

    def _execute(self, command: Command):
        if command == Command.TAKE_OFF:
            self._drone.take_off()
        elif command == Command.LAND:
            self._drone.land()
        elif command == Command.STREAM_ON:
            self._drone
        elif command == Command.STREAM_OFF:
            self._drone

        elif command == Command.MOVE_FORWARD:
            self._drone

        elif command == Command.MOVE_BACKWARD:
            self._drone

        elif command == Command.ROTATE_CW:
            self._drone

        elif command == Command.ROTATE_CCW:
            self._drone

        elif command == Command.FOLLOW_ME:
            self._drone

        elif command == Command.STOP_EXECUTION:
            self._drone

    def execute(self, command: Command):
        Thread(target=self._execute, args=[command]).start()

    def end(self):
        self._drone.end()

