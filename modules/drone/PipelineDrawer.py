
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

import schedule
from modules.drone.DrawerModule import DrawerFPS, DrawerDroneBattery,\
    DrawerDroneTemperature, DrawerDroneHeight, DrawerDroneWifiSNR


class PipelineDrawer:
    DRAWER_FPS = "FPS"
    DRONE_BATTERY = "BATTERY"
    DRONE_TEMPERATURE = "TEMPERATURE"
    DRONE_HEIGHT = "HEIGHT"
    DRONE_WIFI_SNR = "WIFI_SNR"

    def __init__(self):
        self.pipeline = []
        self.len_pipeline = 0

        self.schedule = schedule.Scheduler()

        self.font_scale = 1
        self.w = 10
        self.h = 15 + ((self.font_scale-1) * 0.5)
        self.color = (0, 0, 255)
        self.thickness = 1

    def build(self, drone, drawers):
        for drawer in drawers:
            if drawer == PipelineDrawer.DRAWER_FPS:
                self.add_drawer(drone, DrawerFPS)
            elif drawer == PipelineDrawer.DRONE_BATTERY:
                self.add_drawer(drone, DrawerDroneBattery)
            elif drawer == PipelineDrawer.DRONE_TEMPERATURE:
                self.add_drawer(drone, DrawerDroneTemperature)
            elif drawer == PipelineDrawer.DRONE_HEIGHT:
                self.add_drawer(drone, DrawerDroneHeight)
            elif drawer == PipelineDrawer.DRONE_WIFI_SNR:
                self.add_drawer(drone, DrawerDroneWifiSNR)

    def add_drawer(self, drone, drawer):
        self.len_pipeline = self.len_pipeline + 1
        position = (self.w, int(self.h * self.len_pipeline))
        self.pipeline.append(drawer(self.schedule, drone, position, self.font_scale, self.color, self.thickness))

    def draw(self, frame):
        self.schedule.run_pending()

        for drawer in self.pipeline:
            frame = drawer.draw(frame)
        return frame

    def end(self):
        self.schedule.clear()


if __name__ == "__main__":
    import cv2
    import time
    from modules.drone.DroneModule import FakeDrone
    import platform

    input_idx = 0
    capture_api = None
    if platform.system() == 'Windows':
        input_idx = 1
        capture_api = cv2.CAP_DSHOW


    drone = FakeDrone(input_idx=input_idx, capture_api=capture_api)


    pd = PipelineDrawer()
    pd.build(drone,
                  [PipelineDrawer.DRAWER_FPS,
                   PipelineDrawer.DRONE_BATTERY,
                   PipelineDrawer.DRONE_TEMPERATURE,
                   PipelineDrawer.DRONE_HEIGHT,])
                   #PipelineDrawer.DRONE_WIFI_SNR])
    try:
        while True:
            print(pd.pipeline[3].height)
            print(pd.pipeline[4].snr)
            time.sleep(0.5)
    finally:
        pd.end()

