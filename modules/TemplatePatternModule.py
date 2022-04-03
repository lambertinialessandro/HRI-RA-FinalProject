from abc import ABC, abstractmethod
import cv2
import time
import schedule
from threading import Lock

from modules.control.ControlModule import Command
from modules.face_tracking.FaceTrackingModule import FaceTrackingModule


class AbstractTemplatePattern(ABC):
    def __init__(self, video_stream_module, command_recognition, control_module):
        self.video_stream_module = video_stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module
        self.mutex = Lock()

    @classmethod
    @abstractmethod
    def execute(cls):
        pass


class VideoTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module, drone):
        super().__init__(video_stream_module, command_recognition, control_module)
        self.drone = drone
        self.battery = drone.battery
        schedule.every(10).seconds.do(self.__update_battery)

        self.command = None

        self.pTime = 0
        self.cTime = 0

    def __update_battery(self):
        self.battery = self.drone.battery

    def execute(self):
        try:
            while True:
                schedule.run_pending()  # update the battery if 10 seconds have passed

                # 1. Get the frame
                frame = self.video_stream_module.get_stream_frame()

                # 2. Get the command
                self.command, value = self.command_recognition.get_command(frame)

                # 3. Execute the comand
                if not self.mutex.locked() and self.command:
                    if self.command == Command.LAND:
                        self.mutex.acquire()

                    print(f"Command: {self.command} Value: {value}")

                    self.control_module.execute(self.command, value)
                    self.command = None

                self.cTime = time.time()
                fps = int(1/(self.cTime - self.pTime))
                self.pTime = self.cTime

                cv2.putText(frame, f"Battery: {self.battery}%", (10, 15),
                            cv2.FONT_HERSHEY_PLAIN, fontScale=1,
                            color=(0, 0, 255), thickness=1)
                cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_PLAIN,
                            fontScale=1, color=(0, 0, 255), thickness=1)

                cv2.imshow("Video", frame)

                key = cv2.waitKey(1)
                if key == 27:  # ESC
                    break
                elif key == ord('t'):
                    self.control_module.execute(Command.TAKE_OFF)
                elif key == ord('l'):
                    self.control_module.execute(Command.LAND)
        except KeyboardInterrupt:
            pass
        finally:
            print("Done!")
            cv2.destroyAllWindows()
            self.video_stream_module.release_stream()
            self.control_module.end()
            schedule.clear()


class AudioTemplatePattern(AbstractTemplatePattern):
    def __init__(self, audio_stream_module, command_recognition, control_module, drone):
        super().__init__(audio_stream_module, command_recognition, control_module)
        self.drone = drone
        self.battery = drone.battery
        schedule.every(10).seconds.do(self.__update_battery)

    def __update_battery(self):
        self.battery = self.drone.battery
        print(f"Battery: {self.battery}%")

    def execute(self):
        try:
            while True:
                schedule.run_pending()  # update the battery if 10 seconds have passed

                word = self.audio_stream_module.get_stream_word()
                command = self.command_recognition.get_command(word)
                self.control_module.execute(command)

                if command == Command.STOP_EXECUTION:
                    print("Done!")
                    break
        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()
            self.audio_stream_module.release_stream()
            self.control_module.end()
            schedule.clear()
