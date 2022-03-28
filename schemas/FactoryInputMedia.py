# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:19:26 2022

@author: lambe
"""

import cv2

from InputMedia import VideoDroneInputMedia, VideoPCInputMedia, AudioPCInputMedia


class FactoryInputMedia:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    def createInput(self, typeInputMedia):
        inputMedia = None
        if typeInputMedia == self.VideoDrone:
            inputMedia = VideoDroneInputMedia()
        if typeInputMedia == self.VideoPC:
            inputMedia = VideoPCInputMedia()
        if typeInputMedia == self.AudioPC:
            inputMedia = AudioPCInputMedia()

        return inputMedia

if __name__ == "__main__":
    fim = FactoryInputMedia()
    inputMedia = fim.createInput(FactoryInputMedia.VideoPC)

    try:
        while True:
            success, img = inputMedia.getStream()
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
    finally:
        inputMedia.releasStream()
        cv2.destroyAllWindows()



