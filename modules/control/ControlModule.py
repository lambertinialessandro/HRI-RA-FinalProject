
from enum import Enum
from threading import Thread

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.drone.DroneModule import AbstractDrone as Drone


class Command(Enum):
    NONE = 0

    TAKE_OFF = 1
    LAND = 2
    STREAM_ON = 3
    STREAM_OFF = 4

    MOVE_FORWARD = 10
    MOVE_BACKWARD = 20
    MOVE_UP = 11
    MOVE_DOWN = 12

    SET_RC = 29

    ROTATE_CW = 30
    ROTATE_CCW = 40

    COOLING_ON = 50
    COOLING_OFF = 51

    FOLLOW_ME = 100

    STOP_EXECUTION = 1000

    def __str__(self):
        return self.name


class ControlModule:
    def __init__(self, drone: Drone):
        self._drone = drone

    def __execute(self, command: Command, value=None):
        if not self._drone.is_flying and command != Command.TAKE_OFF:
            return

        if command == Command.NONE:
            pass
        elif command == Command.TAKE_OFF:
            self._drone.take_off()
        elif command == Command.LAND:
            self._drone.land()
        elif command == Command.STREAM_ON:
            self._drone.streamon()
        elif command == Command.STREAM_OFF:
            self._drone.streamoff()

        elif command == Command.MOVE_FORWARD:
            self._drone.move_forward(value)
        elif command == Command.MOVE_BACKWARD:
            self._drone.move_backward(value)
        elif command == Command.MOVE_UP:
            self._drone.move_up(value)
        elif command == Command.MOVE_DOWN:
            self._drone.move_down(value)

        elif command == Command.SET_RC:
            self._drone.set_rc_controls(*value)

        elif command == Command.ROTATE_CW:
            self._drone.rotate_cw(value)
        elif command == Command.ROTATE_CCW:
            self._drone.rotate_ccw(value)

        elif command == Command.COOLING_ON:
            self._drone.turn_motor_on()
        elif command == Command.COOLING_OFF:
            self._drone.turn_motor_off()

        elif command == Command.FOLLOW_ME:
            self._drone

        elif command == Command.STOP_EXECUTION:
            self._drone

    def execute(self, command: Command, value=None):
        Thread(target=self.__execute, args=[command, value]).start()

    def end(self):
        #self._drone.end()
        pass

