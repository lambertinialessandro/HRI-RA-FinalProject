# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:28:45 2022

@author: lambe
"""

from abc import ABC, abstractclassmethod

import cv2


class AbstractInputMedia(ABC):
    def __init__(self):
        pass

    @abstractclassmethod
    def getStream(self):
        pass

    @abstractclassmethod
    def releasStream(self):
        pass


class VideoDroneInputMedia(AbstractInputMedia):
    def __init__(self):
        super.__init__(self)

    def getStream(self):
        return self

    def releasStream(self):
        pass


class VideoPCInputMedia(AbstractInputMedia):
    def __init__(self):
        super().__init__()

        self.inputIdx = 0
        self.w = 1280//2
        self.h = 720//2

        self.cap = cv2.VideoCapture(self.inputIdx, cv2.CAP_DSHOW)
        self.cap.set(3, self.w)
        self.cap.set(4, self.h)

    def getStream(self):
        return self.cap.read()

    def releasStream(self):
        self.cap.release()

class AudioPCInputMedia(AbstractInputMedia):
    def __init__(self):
        super.__init__(self)

    def getStream(self):
        return []

    def releasStream(self):
        pass
