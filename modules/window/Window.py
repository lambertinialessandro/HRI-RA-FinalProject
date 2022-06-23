import cv2
import keyboard

from modules.command_recognition.CommandRecognitionFactory import \
    VideoCommandRecognitionFactory as vrf, VCREnum


import matplotlib.pyplot as plt

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
            #elif keyboard_event.name == "u":
            #    self._binded_obj.drone.move_up(30)
            #elif keyboard_event.name == "d":
            #    self._binded_obj.drone.move_down(30)
            elif keyboard_event.name == "0":
                print("Empty!")
                self._binded_obj.command_recognition = vrf.create(VCREnum.Empty)
            elif keyboard_event.name == "1":
                print("Face!")
                self._binded_obj.command_recognition = vrf.create(VCREnum.Face)
            elif keyboard_event.name == "2":
                print("Hand!")
                self._binded_obj.command_recognition = vrf.create(VCREnum.Hand)
            elif keyboard_event.name == "3":
                print("Holistic!")
                self._binded_obj.command_recognition = vrf.create(VCREnum.Holistic)
            elif keyboard_event.name == "4":
                print("Holistic RA!")
                self._binded_obj.command_recognition = vrf.create(VCREnum.Holistic_RA)

            elif keyboard_event.scan_code == 72: # name == "freccia su"
                self._binded_obj.drone.set_rc_controls(0, 10, 0, 0)
            elif keyboard_event.scan_code == 80: # name == "freccia giù"
                self._binded_obj.drone.set_rc_controls(0, -10, 0, 0)
            elif keyboard_event.scan_code == 75: # name == "freccia sinistra"
                self._binded_obj.drone.set_rc_controls(0, 0, 0, 20)
            elif keyboard_event.scan_code == 77: # name == "freccia destra"
                self._binded_obj.drone.set_rc_controls(0, 0, 0, -20)
            elif keyboard_event.name == "p": # name == "freccia sinistra"
                self._binded_obj.drone.set_rc_controls(0, 0, 20, 0)
            elif keyboard_event.name == "o": # name == "freccia destra"
                self._binded_obj.drone.set_rc_controls(0, 0, -20, 0)
            elif keyboard_event.name == "space": # 57
                self._binded_obj.drone.set_rc_controls(0, 0, 0, 0)


            elif keyboard_event.name == "w":
                self._binded_obj.drone.move_forward(30)
            elif keyboard_event.name == "s":
                self._binded_obj.drone.move_backward(30)
            elif keyboard_event.name == "a":
                self._binded_obj.drone.move_left(30)
            elif keyboard_event.name == "d":
                self._binded_obj.drone.move_right(30)
            elif keyboard_event.name == "e":
                self._binded_obj.drone.rotate_cw(30)
            elif keyboard_event.name == "q":
                self._binded_obj.drone.rotate_ccw(30)
            elif keyboard_event.name == "r":
                self._binded_obj.drone.move_up(30)
            elif keyboard_event.name == "f":
                self._binded_obj.drone.move_down(30)

            #elif keyboard_event.name == "p":
            #    plt.show()


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
