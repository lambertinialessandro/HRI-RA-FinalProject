import cv2
import keyboard

from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory


class Window:
    instance = None

    def bind(self, cls):
        self.cls = cls

    def __new__(self, *args, **kwargs):
         if Window.instance == None:
             Window.instance = super(Window, self).__new__(self)
         return Window.instance

    def __init__(self, cls=None, name="Video"):
        self.bind(cls)
        self.name = name
        cv2.namedWindow(name)

        def my_keyboard_hook(keyboard_event):
            # print("Name:", keyboard_event.name)
            # print("Scan code:", keyboard_event.scan_code)
            # print("Time:", keyboard_event.time)

            #if keyboard_event.name == "esc":
            #    self.cls.end()
            #el
            if keyboard_event.name == "l":
                self.cls.drone.land()
            elif keyboard_event.name == "t":
                self.cls.drone.take_off()
            elif keyboard_event.name == "u":
                self.cls.drone.move_up(10)
            elif keyboard_event.name == "d":
                self.cls.drone.move_down(10)

            elif keyboard_event.name == "1":
                print("Face!")
                self.cls.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoFace)
            elif keyboard_event.name == "2":
                print("Hand!")
                self.cls.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoHand)
            # elif keyboard_event.name == "3":
            #     print("Holistic!")
            #     self.update_detector(VideoTrackingFactory.Holistic)

        keyboard.on_press(my_keyboard_hook)

    def show(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            return False
        return True

    def end(self):
        Window.instance = None

        keyboard.unhook_all()
        cv2.destroyAllWindows()
