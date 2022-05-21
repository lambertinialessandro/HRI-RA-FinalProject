import cv2
import keyboard

from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory


class Window:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if Window._instance is None:
            Window._instance = super(Window, cls).__new__(cls)
        return Window._instance

    def __init__(self, binded_obj=None, name="Video"):
        self._binded_obj = binded_obj
        self.name = name
        cv2.namedWindow(name)

        def my_keyboard_hook(keyboard_event):
            # print("Name:", keyboard_event.name)
            # print("Scan code:", keyboard_event.scan_code)
            # print("Time:", keyboard_event.time)

            #if keyboard_event.name == "esc":
            #    self._binded_obj.end()
            #el
            if keyboard_event.name == "l":
                self._binded_obj.drone.land()
            elif keyboard_event.name == "t":
                self._binded_obj.drone.take_off()
            elif keyboard_event.name == "u":
                self._binded_obj.drone.move_up(30)
            elif keyboard_event.name == "d":
                self._binded_obj.drone.move_down(30)

            elif keyboard_event.name == "1":
                print("Face!")
                self._binded_obj.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoFace)
            elif keyboard_event.name == "2":
                print("Hand!")
                self._binded_obj.command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoHand)
            # elif keyboard_event.name == "3":
            #     print("Holistic!")
            #     self.update_detector(VideoTrackingFactory.Holistic)

            elif keyboard_event.scan_code == 72: # name == "freccia su"
                self._binded_obj.drone.set_rc_controls(0, 10, 0, 0)
            elif keyboard_event.scan_code == 80: # name == "freccia giù"
                self._binded_obj.drone.set_rc_controls(0, -10, 0, 0)
            elif keyboard_event.scan_code == 75: # name == "freccia sinistra"
                self._binded_obj.drone.set_rc_controls(0, 0, 0, 20)
            elif keyboard_event.scan_code == 77: # name == "freccia destra"
                self._binded_obj.drone.set_rc_controls(0, 0, 0, -20)
            elif keyboard_event.name == "space": # 57
                self._binded_obj.drone.set_rc_controls(0, 0, 0, 0)

        keyboard.on_press(my_keyboard_hook)

    def show(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            return False
        return True

    def end(self):
        Window._instance = None

        keyboard.unhook_all()
        cv2.destroyAllWindows()
