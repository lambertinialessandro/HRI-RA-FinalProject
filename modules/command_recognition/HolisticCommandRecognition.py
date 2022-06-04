import math
import time
import mediapipe as mp
import cv2

import sys
sys.path.append('../../')

from modules.command_recognition.HandCommandRecognition import HandEnum
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


class HolisticCommandRecognition(AbstractCommandRecognitionModule):
    def __init__(self, static_image_mode=False, model_complexity=1,
                 smooth_landmarks=True, enable_segmentation=False,
                 smooth_segmentation=True, refine_face_landmarks=True,
                 min_tracking_confidence=.5, min_detection_confidence=.5,
                 flip_type=True):
        super().__init__()
        self.flip_type = flip_type

        self.holistic_detection = mp.solutions.holistic.Holistic(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            smooth_segmentation=smooth_segmentation,
            refine_face_landmarks=refine_face_landmarks,
            min_tracking_confidence=min_tracking_confidence,
            min_detection_confidence=min_detection_confidence
        )
        self.data = []

    def _analyze_frame(self, frame):
        return self.holistic_detection.process(frame)

    def _execute(self, data) -> tuple:
        self.data = data
        command = Command.NONE, None
        # TODO
        return command

    def edit_frame(self, frame):
        # TODO
        return frame

    def end(self):
        pass


class HolisticRACommandRecognition(HolisticCommandRecognition):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.state = 0
        self.init_t = time.time()

    def _execute(self, data) -> tuple:
        command = Command.NONE, None

        if self.state == 0:  # Inactive
            elapsed_t = time.time() - self.init_t
            if elapsed_t > 3:
                self.state = 1
                command = Command.TAKE_OFF, None

        elif self.state == 1:  # Searching
            if data:
                # TODO : if resoults for 2 seconds
                self.state = 2
            else:
                command = Command.ROTATE_CW, 30

        elif self.state == 2:  # Following
            pass # TODO follow as in face

        elif self.state == 3:  # Identified
            command = super()._execute(data)

        return command
