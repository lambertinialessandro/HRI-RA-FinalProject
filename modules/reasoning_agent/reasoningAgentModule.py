
from modules.control.ControlModule import Command

class reasoningAgent():
    def __init__(self, drone):
        self.drone = drone

    def execute(self, command, value):
        if self.drone.is_flying:
            if self.drone.battery < 5:
                command = Command.LAND
                value = None
        else:
            if self.drone.temperature > 40 and not self.drone.is_cooling:
                command = Command.COOLING_ON
                value = None
            elif self.drone.temperature < 40 and self.drone.is_cooling:
                command = Command.COOLING_OFF
                value = None

        return command, value