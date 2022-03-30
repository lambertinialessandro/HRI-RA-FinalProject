# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:28:45 2022

@author: lambe
"""

from abc import ABC, abstractmethod
import cv2
from djitellopy import Tello


class VideoStreamModule(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_stream(cls):
        pass

    @classmethod
    @abstractmethod
    def release_stream(cls):
        pass


class VideoDroneStream(VideoStreamModule):
    def __init__(self, tello: Tello):
        super().__init__()
        self.tello = tello

        self.w = 1280//2
        self.h = 720//2

        tello.streamon()
        self.frame_read = tello.get_frame_read()

    def get_stream(self):
        return cv2.resize(self.frame_read.frame, (self.w, self.h))

    def release_stream(self):
        self.frame_read = None
        self.tello.streamoff()


class WebcamStream(VideoStreamModule):
    def __init__(self):
        super().__init__()

        self.inputIdx = 0
        self.w = 1280//2
        self.h = 720//2

        self.cap = cv2.VideoCapture(self.inputIdx)#, cv2.CAP_DSHOW)
        # self.cap.set(3, self.w)
        # self.cap.set(4, self.h)

    def get_stream(self):
        _, frame = self.cap.read()
        return frame

    def release_stream(self):
        self.cap.release()
