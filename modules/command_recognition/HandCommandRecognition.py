
import math
from abc import abstractmethod
import mediapipe as mp
import cv2
import time

import sys
sys.path.append('../')

from modules.command_recognition.model.keypoint_classifier import HandGesture
from modules.command_recognition.HandGestureModule import HandGestureRecognizer, Hand
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule
from modules.control.ControlModule import Command


class AbstractMediaPipeHandCommandRecognition(AbstractCommandRecognitionModule):
    def __init__(self, mode=False, max_hands=2, detection_con=.5, track_con=.5, flip_type=True):
        super().__init__()
        self.flip_type = flip_type
        self.max_hands = max_hands

        self.all_hands = []
        self.hand_detection = mp.solutions.hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )

    def _analyze_frame(self, frame):
        self.all_hands = []

        results = self.hand_detection.process(frame)

        if results.multi_hand_landmarks:
            h, w, c = frame.shape
            for handType, handLms in zip(results.multi_handedness, results.multi_hand_landmarks):
                mylm_list = []
                x_list = []
                y_list = []

                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = lm.x, lm.y, lm.x
                    mylm_list.append([px, py, pz])
                    x_list.append(px)
                    y_list.append(py)

                xmin, xmax = min(x_list), max(x_list)
                ymin, ymax = min(y_list), max(y_list)
                boxW = xmax - xmin
                boxH = ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx = bbox[0] + (bbox[2] // 2)
                cy = bbox[1] + (bbox[3] // 2)

                hand = Hand(
                    center=(cx, cy),
                    bbox=bbox,
                    lmList=mylm_list,
                    type=Hand.HandType.RIGHT
                )

                if self.flip_type:
                    if handType.classification[0].label.lower() == "right":
                        hand.type = Hand.HandType.RIGHT
                    else:
                        hand.type = Hand.HandType.LEFT
                else:
                    hand.type = handType.classification[0].label
                self.all_hands.append(hand)

    @abstractmethod
    def _execute(self) -> tuple:
        pass

    @abstractmethod
    def edit_frame(self, frame):
        pass

    def end(self):
        pass


class MediaPipeHandCommandRecognition(AbstractMediaPipeHandCommandRecognition):
    def __init__(self, mode=False, max_hands=2, detection_con=.5, track_con=.5, flip_type=True):
        super().__init__(mode=mode, max_hands=max_hands, detection_con=detection_con,
                         track_con=track_con, flip_type=flip_type)
        self.gesture, self.value = HandGesture.NONE, 0
        self.old_gesture = Command.NONE
        self.time_g = time.time()

    def _execute(self) -> tuple:
        command, value = Command.NONE, None
        r_hand = self._get_hands_info(Hand.HandType.RIGHT)
        l_hand = self._get_hands_info(Hand.HandType.LEFT)

        self.gesture, self.value = HandGestureRecognizer.execute(l_hand, r_hand)
        if self.value >= 30:
            if self.gesture == HandGesture.FORWARD:
                command, value = Command.MOVE_FORWARD, self.value
            elif self.gesture == HandGesture.UP:
                command, value = Command.MOVE_UP, self.value
            elif self.gesture == HandGesture.LAND:
                command, value = Command.LAND, self.value
            elif self.gesture == HandGesture.DOWN:
                command, value = Command.MOVE_DOWN, self.value
            elif self.gesture == HandGesture.BACK:
                command, value = Command.MOVE_BACKWARD, self.value
            elif self.gesture == HandGesture.LEFT:
                command, value = Command.MOVE_LEFT, self.value
            elif self.gesture == HandGesture.RIGHT:
                command, value = Command.MOVE_RIGHT, self.value
        if self.gesture == HandGesture.STOP:
            command, value = Command.SET_RC, (0, 0, 0, 0)

        elapsed_t = time.time() - self.time_g
        if self.old_gesture == command and self.gesture != HandGesture.NONE and command != Command.NONE:
            if elapsed_t > 2:
                self.time_g = time.time()
                self.old_gesture = HandGesture.NONE
                return command, value
        else:
            self.old_gesture = command
            if elapsed_t > 2:
                self.time_g = time.time()
                return Command.KEEP_ALIVE, None

        return Command.NONE, None

    def edit_frame(self, frame):
        r_hand = self._get_hands_info(Hand.HandType.RIGHT)
        l_hand = self._get_hands_info(Hand.HandType.LEFT)
        frame = HandGestureRecognizer.edit_frame(frame, l_hand, r_hand,
                                                 self.gesture, self.value)

        return frame

    def _get_hands_info(self, t: Hand.HandType):
        if t == Hand.HandType.LEFT or t == Hand.HandType.RIGHT:
            for hand in self.all_hands:
                if hand.type == t:
                    return hand
        else:
            raise ValueError(t)

    def end(self):
        pass
