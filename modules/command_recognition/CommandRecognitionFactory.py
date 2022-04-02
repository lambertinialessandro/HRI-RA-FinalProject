# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:41:12 2022

@author: lambe
"""

import sys

from modules.command_recognition.VideoCommandRecognitionModule import VideoCommandRecognition
from modules.command_recognition.AudioCommandRecognitionModule import AudioCommandRecognition

sys.path.append('../../')


class CommandRecognitionFactory:
    Video = "Video"
    Audio = "Audio"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition = None
        if type_input == CommandRecognitionFactory.Video:
            command_recognition = VideoCommandRecognition()
        elif type_input == CommandRecognitionFactory.Audio:
            command_recognition = AudioCommandRecognition()

        return command_recognition


if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, CaptureAPI=cv2.CAP_DSHOW) # cv2.CAP_DSHOW, None
    command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)

    try:
        while True:
            frame = stream.get_stream_frame()
            command = command_recognition.get_command(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()