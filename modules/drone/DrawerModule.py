
import cv2
import schedule
import time
from abc import ABC, abstractmethod


class AbstractDrawer(ABC):
    def __init__(self, drone, position, font_scale, color, thickness):
        self.drone = drone
        self.position = position
        self.font_scale = font_scale
        self.color = color
        self.thickness = thickness

    @abstractmethod
    def draw(self, frame):
        pass


class DrawerFPS(AbstractDrawer):
    def __init__(self, drone, position, font_scale, color, thickness):
        super().__init__(drone, position, font_scale, color, thickness)

        self.pTime = 0
        self.cTime = 0

    def draw(self, frame):
        self.cTime = time.time()
        elapsed = self.cTime - self.pTime
        if elapsed == 0:
            fps = 0
        else:
            fps = int(1/(self.cTime - self.pTime))
        self.pTime = self.cTime

        cv2.putText(frame, f"FPS: {fps}", self.position, cv2.FONT_HERSHEY_PLAIN,
                    fontScale=self.font_scale, color=self.color, thickness=self.thickness)
        return frame


class DrawerDroneBattery(AbstractDrawer):
    def __init__(self, drone, position, font_scale, color, thickness):
        super().__init__(drone, position, font_scale, color, thickness)

        self.battery = None
        self._update_battery()
        schedule.every(10).seconds.do(self._update_battery)

    def _update_battery(self):
        self.battery = self.drone.battery

    def draw(self, frame):
        cv2.putText(frame, f"Battery: {self.battery}%", self.position, cv2.FONT_HERSHEY_PLAIN,
                    fontScale=self.font_scale, color=self.color, thickness=self.thickness)
        return frame


class DrawerDroneTemperature(AbstractDrawer):
    def __init__(self, drone, position, font_scale, color, thickness):
        super().__init__(drone, position, font_scale, color, thickness)

        self.temperature = None
        self._update_temperature()
        schedule.every(5).seconds.do(self._update_temperature)

    def _update_temperature(self):
        self.temperature = self.drone.temperature

    def draw(self, frame):
        cv2.putText(frame, f"temperature: {self.temperature} 'C", self.position, cv2.FONT_HERSHEY_PLAIN,
                    fontScale=self.font_scale, color=self.color, thickness=self.thickness)
        return frame


class DrawerDroneHeight(AbstractDrawer):
    def __init__(self, drone, position, font_scale, color, thickness):
        super().__init__(drone, position, font_scale, color, thickness)

        self.height = None
        self._update_height()
        schedule.every(1).seconds.do(self._update_height)

    def _update_height(self):
        self.height = self.drone.height

    def draw(self, frame):
        cv2.putText(frame, f"Height: {self.height}", self.position, cv2.FONT_HERSHEY_PLAIN,
                    fontScale=self.font_scale, color=self.color, thickness=self.thickness)
        return frame


class DrawerDroneWifiSNR(AbstractDrawer):
    def __init__(self, drone, position, font_scale, color, thickness):
        super().__init__(drone, position, font_scale, color, thickness)

        self.snr = None
        self._update_snr()
        schedule.every(5).seconds.do(self._update_snr)

    def _update_snr(self):
        self.snr = self.drone.wifi_snr

    def draw(self, frame):
        cv2.putText(frame, f"wifi snr: {self.snr}", self.position, cv2.FONT_HERSHEY_PLAIN,
                    fontScale=self.font_scale, color=self.color, thickness=self.thickness)
        return frame

