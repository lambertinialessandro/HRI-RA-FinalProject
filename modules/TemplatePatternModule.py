# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 12:04:21 2022

@author: lambe
"""

from abc import ABC, abstractmethod
import cv2
import schedule

from modules.control.ControlModule import Command

class AbstractTemplatePattern(ABC):
    def __init__(self, video_stream_module, command_recognition, control_module):
        self.video_stream_module = video_stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module

    @classmethod
    @abstractmethod
    def execute(cls):
        pass


class VideoTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module):
        super().__init__(video_stream_module, command_recognition, control_module)

    def execute(self):
        try:
            while True:
                # schedule.run_pending()  # update the battery if 10 seconds have passed

                frame = self.video_stream_module.get_stream_frame()
                command = self.command_recognition.get_command(frame)
                self.control_module.execute(command)

                # cv2.putText(frame, f"Battery: {battery}%", (10, 15), cv2.FONT_HERSHEY_PLAIN, fontScale=1,
                #             color=(0, 0, 255), thickness=1)
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
            cv2.destroyAllWindows()
            self.video_stream_module.release_stream()
            self.control_module.end()


class AudioTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module):
        super().__init__(video_stream_module, command_recognition, control_module)

    def execute(self):
        try:
            while True:
                # schedule.run_pending()  # update the battery if 10 seconds have passed

                word = self.video_stream_module.get_stream_word()
                command = self.command_recognition.get_command(word)
                self.control_module.execute(command)

                # print(battery)
        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()
            self.video_stream_module.release_stream()
            self.control_module.end()