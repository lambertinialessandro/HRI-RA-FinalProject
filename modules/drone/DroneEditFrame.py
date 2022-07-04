
from modules.drone.PipelineDrawer import PipelineDrawer


class DroneEditFrame:
    def __init__(self, drone):
        self.pd = PipelineDrawer()
        self.pd.build(drone,
                      [PipelineDrawer.DRAWER_FPS,
                       PipelineDrawer.DRONE_BATTERY,
                       PipelineDrawer.DRONE_TEMPERATURE,
                       PipelineDrawer.DRONE_HEIGHT,])

    def edit(self, frame):
        frame = self.pd.draw(frame)
        return frame

    def end(self):
        self.pd.end()