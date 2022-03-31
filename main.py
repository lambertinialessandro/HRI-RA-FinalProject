#!/usr/local/bin/python3

import cv2
import schedule

from modules.DroneFactory import DroneFactory
from modules.GlobalFactory import GlobalFactory

from modules.control.ControlModule import Command



from abc import ABC, abstractmethod
class AbstractTemplatePattern(ABC):
    def __init__(self, video_stream_module, command_recognition, control_module):
        self.video_stream_module = video_stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module

    @classmethod
    @abstractmethod
    def execute(self):
        pass

class VideoTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module):
        super().__init__(video_stream_module, command_recognition, control_module)

    def execute(self):
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

class AudioTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module):
        super().__init__(video_stream_module, command_recognition, control_module)

    def execute(self):
        try:
            while True:
                schedule.run_pending()  # update the battery if 10 seconds have passed


                word = video_stream_module.get_stream_word()
                command = command_recognition.get_command(word)
                control_module.execute(command)

                print(battery)



        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()
            video_stream_module.release_stream()
            control_module.end()






df = DroneFactory()
drone = df.create(DroneFactory.FakeDrone, CaptureAPI=cv2.CAP_DSHOW)

battery = drone.battery
schedule.every(10).seconds.do(lambda: globals().__setitem__("battery", drone.battery))

type_input = GlobalFactory.AudioPC
gf = GlobalFactory()
video_stream_module, command_recognition, control_module = gf.create(type_input, drone)

if type_input == GlobalFactory.VideoDrone or type_input == GlobalFactory.VideoPC:
    tp = VideoTemplatePattern(video_stream_module, command_recognition, control_module)
elif type_input == GlobalFactory.AudioPC:
    tp = AudioTemplatePattern(video_stream_module, command_recognition, control_module)


tp.execute()






