# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:09:20 2022

@author: lambe
"""

from abc import ABC, abstractmethod
import cv2
import time

class AbstractVideoCommandRecognition(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_command(cls):
        pass


class VideoCommandRecognition(AbstractVideoCommandRecognition):
    def __init__(self):
        super().__init__()
        self.pTime = 0
        self.cTime = 0

    def get_command(self, frame):
        self.cTime = time.time()
        fps = int(1/(self.cTime - self.pTime))
        self.pTime = self.cTime

        cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)

        return None