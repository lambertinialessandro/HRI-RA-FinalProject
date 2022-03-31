#!/usr/local/bin/python3

import cv2
import schedule

from modules.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory


from modules.control.ControlModule import Command


df = DroneFactory()
drone = df.create(DroneFactory.FakeDrone, CaptureAPI=cv2.CAP_DSHOW)

battery = drone.battery
schedule.every(10).seconds.do(lambda: globals().__setitem__("battery", drone.battery))

gf = GlobalFactory()
video_stream_module, command_recognition, control_module = gf.create(GlobalFactory.VideoDrone, drone)

try:
    while True:
        schedule.run_pending()  # update the battery if 10 seconds have passed

        frame = video_stream_module.get_stream_frame()
        command = command_recognition.get_command(frame)
        control_module.execute(command)

        cv2.putText(frame, f"Battery: {battery}%", (10, 15), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
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
