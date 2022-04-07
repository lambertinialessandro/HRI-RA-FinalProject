import cv2
import keyboard

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

        def my_keyboard_hook(keyboard_event):
            print("Name:", keyboard_event.name)
            print("Scan code:", keyboard_event.scan_code)
            print("Time:", keyboard_event.time)

            if keyboard_event.name == "t":
                drone.take_off()
            elif keyboard_event.name == "l":
                drone.land()

            # if keyboard_event.name == "1":
            #     print("Face!")
            #     self.update_detector(VideoTrackingFactory.Face)
            # elif keyboard_event.name == "2":
            #     print("Hand!")
            #     self.update_detector(VideoTrackingFactory.Hand)
            # elif keyboard_event.name == "3":
            #     print("Holistic!")
            #     self.update_detector(VideoTrackingFactory.Holistic)

        keyboard.hook(my_keyboard_hook)

        Window.instance = self

    def show(self, frame):
        self.pd.draw(frame)

        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            self.on_closed()

    def destroy(self):
        Window.instance = None

        keyboard.unhook_all()
        cv2.destroyAllWindows()
