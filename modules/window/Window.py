import cv2

from modules.DrawerModule import PipelineDrawerBuilder


class Window:
    instance = None

    def __init__(self, drone, on_closed, name="Video"):
        self.on_closed = on_closed
        self.name = name

        self.pd = PipelineDrawerBuilder.build(drone,
                                              [PipelineDrawerBuilder.DRAWER_FPS,
                                               PipelineDrawerBuilder.DRONE_BATTERY,
                                               PipelineDrawerBuilder.DRONE_TEMPERATURE,
                                               PipelineDrawerBuilder.DRONE_HEIGHT])

        cv2.namedWindow(self.name)

        Window.instance = self

    def show(self, frame):
        self.pd.draw(frame)

        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            self.on_closed()

    def destroy(self):
        Window.instance = None
        cv2.destroyAllWindows()
