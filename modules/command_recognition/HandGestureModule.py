import dataclasses
from enum import Enum
import math
import cv2

from modules.command_recognition.model.keypoint_classifier import KeyPointClassifier, HandGesture


@dataclasses.dataclass
class Hand:
    class HandType(Enum):
        LEFT = "left"
        RIGHT = "right"

    center: tuple
    bbox: tuple
    lmList: list
    type: HandType

    class Keypoints(Enum):
        WRIST = 0
        THUMB_CMC = 1
        THUMB_MCP = 2
        THUMB_IP = 3
        THUMB_TIP = 4
        INDEX_FINGER_MCP = 5
        INDEX_FINGER_PIP = 6
        INDEX_FINGER_DIP = 7
        INDEX_FINGER_TIP = 8
        MIDDLE_FINGER_MCP = 9
        MIDDLE_FINGER_PIP = 10
        MIDDLE_FINGER_DIP = 11
        MIDDLE_FINGER_TIP = 12
        RING_FINGER_MCP = 13
        RING_FINGER_PIP = 14
        RING_FINGER_DIP = 15
        RING_FINGER_TIP = 16
        PINKY_MCP = 17
        PINKY_PIP = 18
        PINKY_DIP = 19
        PINKY_TIP = 20

        def tips(self):
            return [self.THUMB_TIP.value, self.INDEX_FINGER_TIP.value,
                    self.MIDDLE_FINGER_TIP.value, self.RING_FINGER_TIP.value,
                    self.PINKY_TIP.value]


class HandGestureRecognizer:
    _keypointClassifier = KeyPointClassifier()

    @staticmethod
    def execute(left_hand: Hand, right_hand: Hand) -> tuple:
        hand_sign = HandGesture.NONE
        value = 0

        if right_hand:
            hand_sign = HandGestureRecognizer._keypointClassifier.classify(right_hand.lmList)

        if left_hand:
            (ttx, tty, ttz) = left_hand.lmList[Hand.Keypoints.THUMB_TIP.value]
            (itx, ity, itz) = left_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]

            distance = math.dist((ttx, tty), (itx, ity))

            (wx, wy, wz) = left_hand.lmList[Hand.Keypoints.WRIST.value]
            dist = math.dist((wx, wy), (itx, ity))
            delta = (dist/10)
            value = int(distance // delta)
            if value != 0:
                value = 30 + 5 * value

        return hand_sign, value

    @staticmethod
    def edit_frame(frame, left_hand: Hand, right_hand: Hand, gesture, value):
        h, w, c = frame.shape

        if right_hand:
            bbox = right_hand.bbox
            bbox = int(right_hand.bbox[0]*w), int(right_hand.bbox[1]*h),\
                int(right_hand.bbox[2]*w), int(right_hand.bbox[3]*h)
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, str(gesture.value), (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        if left_hand:
            (ttx, tty, ttz) = left_hand.lmList[Hand.Keypoints.THUMB_TIP.value]
            (itx, ity, itz) = left_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]

            cv2.line(frame, (int(ttx*w), int(tty*h)), (int(itx*w), int(ity*h)), (255, 0, 255), 2)
            cv2.putText(frame, str(value), (int(itx*w), int(ity*h)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        return frame


