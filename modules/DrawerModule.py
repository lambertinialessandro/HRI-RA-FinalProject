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


class PipelineDrawer:
    def __init__(self):
        self.pipeline = []
        self.len_pipeline = 0

        self.font_scale = 1
        self.w = 10
        self.h = 15 + ((self.font_scale-1) * 0.5)
        self.color = (0, 0, 255)
        self.thickness = 1

    def addDrawer(self, drone, drawer):
        self.len_pipeline = self.len_pipeline + 1
        position = (self.w, int(self.h * self.len_pipeline))
        self.pipeline.append(drawer(drone, position, self.font_scale, self.color, self.thickness))

    def draw(self, frame):
        for drawer in self.pipeline:
            frame = drawer.draw(frame)
        return frame

    def end(self):
        schedule.clear()


class PipelineDrawerBuilder:
    DRAWER_FPS = "FPS"
    DRONE_BATTERY = "BATTERY"
    DRONE_TEMPERATURE = "TEMPERATURE"
    DRONE_HEIGHT = "HEIGHT"

    def __init__(self):
        pass

    @staticmethod
    def build(drone, drawers):
        pd = PipelineDrawer()

        for drawer in drawers:
            if drawer == PipelineDrawerBuilder.DRAWER_FPS:
                pd.addDrawer(drone, DrawerFPS)
            elif drawer == PipelineDrawerBuilder.DRONE_BATTERY:
                pd.addDrawer(drone, DrawerDroneBattery)
            elif drawer == PipelineDrawerBuilder.DRONE_TEMPERATURE:
                pd.addDrawer(drone, DrawerDroneTemperature)
            elif drawer == PipelineDrawerBuilder.DRONE_HEIGHT:
                pd.addDrawer(drone, DrawerDroneHeight)

        return pd