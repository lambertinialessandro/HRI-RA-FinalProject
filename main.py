#!/usr/local/bin/python3
from modules import drone
from modules.factories.GlobalFactory import GlobalFactory

from modules.ControlModule import Command

import cv2
import schedule


tello = drone.DJITello()
battery = tello.battery
schedule.every(10).seconds.do(lambda: globals().__setitem__("battery", tello.battery))

fim = GlobalFactory()
video_stream_module, command_recognition, control_module = fim.create_input(GlobalFactory.VideoDrone, tello)

try:
    while True:
        schedule.run_pending()  # update the battery if 10 seconds have passed

        frame = video_stream_module.get_stream_frame()
        cv2.putText(frame, f"Battery: {battery}%", (10, 40), cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(0, 0, 255), thickness=2)
        cv2.imshow("Video", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == ord('t'):
            control_module.execute(Command.TAKE_OFF)
        elif key == ord('l'):
            control_module.execute(Command.LAND)
except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
    video_stream_module.release_stream()
    control_module.end()
