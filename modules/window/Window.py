import cv2
import keyboard

from modules.DrawerModule import PipelineDrawerBuilder
from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory


class Window:
    instance = None

    def __init__(self, cls, name="Video"):
        self.cls = cls

        self.pd = PipelineDrawerBuilder.build(cls.drone,
                                              [PipelineDrawerBuilder.DRAWER_FPS,
                                               PipelineDrawerBuilder.DRONE_BATTERY,
                                               PipelineDrawerBuilder.DRONE_TEMPERATURE,
                                               PipelineDrawerBuilder.DRONE_HEIGHT])

        #cv2.namedWindow(name)

        def my_keyboard_hook(keyboard_event):
            # print("Name:", keyboard_event.name)
            # print("Scan code:", keyboard_event.scan_code)
            # print("Time:", keyboard_event.time)

            if keyboard_event.name == "t":
                cls.drone.take_off()
            elif keyboard_event.name == "l":
                cls.drone.land()
            elif keyboard_event.name == "u":
                cls.drone.move_up(10)
            elif keyboard_event.name == "d":
                cls.drone.move_down(10)

            elif keyboard_event.name == "1":
                print("Face!")
                cls.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoFace)
            elif keyboard_event.name == "2":
                print("Hand!")
                cls.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoHand)
            # elif keyboard_event.name == "3":
            #     print("Holistic!")
            #     self.update_detector(VideoTrackingFactory.Holistic)

        keyboard.on_press(my_keyboard_hook)

        Window.instance = self

    def show(self, frame):
        self.pd.draw(frame)

        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            self.on_closed()

    def end(self):
        Window.instance = None

        keyboard.unhook_all()
        cv2.destroyAllWindows()
