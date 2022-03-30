from abc import ABC
from enum import Enum

from modules.drone import Drone


class Command(Enum):
    TAKE_OFF = 1
    LAND = 2


class ControlModule(ABC):
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self, command: Command):
        if command == Command.TAKE_OFF:
            self._drone.take_off()
        elif command == Command.LAND:
            self._drone.land()

    def end(self):
        self._drone.land()
        self._drone.end()

