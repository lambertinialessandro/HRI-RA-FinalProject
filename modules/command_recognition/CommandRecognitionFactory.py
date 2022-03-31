# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:41:12 2022

@author: lambe
"""

import sys
sys.path.append('../../')

from modules.command_recognition.VideoCommandRecognitionModule import VideoCommandRecognition
#from modules.command_recognition.AudioCommandRecognitionModule import AudioCommandRecognition


class CommandRecognitionFactory:
    Video = "Video"
    Audio = "Audio"

    def __init__(self):
        pass

    def create(self, type_input):
        command_recognition = None
        if type_input == self.Video:
            command_recognition = VideoCommandRecognition()
        # if type_input == self.Audio:
        #     command_recognition = AudioCommandRecognition()

        return command_recognition


if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    sf = StreamFactory()
    stream = sf.create(StreamFactory.VideoPC, CaptureAPI=cv2.CAP_DSHOW) # cv2.CAP_DSHOW, None
    crf = CommandRecognitionFactory()
    command_recognition = crf.create(CommandRecognitionFactory.Video)

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