from abc import ABC
from enum import Enum

from modules.drone import Drone

from threading import Thread


class Command(Enum):
    TAKE_OFF = 1
    LAND = 2


class ControlModule(ABC):
    def __init__(self, drone: Drone):
        self._drone = drone

    def _execute(self, command: Command):
        if command == Command.TAKE_OFF:
            self._drone.take_off()
        elif command == Command.LAND:
            self._drone.land()

    def execute(self, command: Command):
        Thread(target=self._execute, args=[command]).start()

    def end(self):
        try:
            self._drone.land()
        except Exception:
            # Drone has just landed
            pass
        
        self._drone.end()

