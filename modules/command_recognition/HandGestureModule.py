
import dataclasses
from enum import Enum
import math
import cv2

from modules.command_recognition.model.keypoint_classifier import KeyPointClassifier


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


class HandGesture(Enum):
    NONE = 0    # ❌

    FORWARD = 1 # ✋
    STOP = 2    # ✊
    UP = 3      # 👆
    LAND = 4    # 👌
    DOWN = 5    # 👇
    BACK = 6    # 👊
    LEFT = 7    # 👈 thumb
    RIGHT = 8   # 👉 thumb


class HandGestureRecognizer:
    _keypointClassifier = KeyPointClassifier()

    @staticmethod
    def execute(left_hand: Hand, right_hand: Hand) -> tuple:  # Gesture, value
        command = None
        value = 0

        if right_hand:
            hand_sign = HandGestureRecognizer._keypointClassifier.classify(right_hand.lmList)
            print(hand_sign)

        if left_hand:
            (ttx, tty, ttz) = left_hand.lmList[Hand.Keypoints.THUMB_TIP.value]
            (itx, ity, itz) = left_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]

            distance = math.dist((ttx, tty), (itx, ity))
            delta = 0.1 # (1-0)/10 -> (end value - init value) / num steps
            value = distance // delta

        return hand_sign, value

    @staticmethod
    def edit_frame(frame, left_hand: Hand, right_hand: Hand, gesture):

        if right_hand:
            bbox = right_hand.bbox
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, str(gesture), (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        if left_hand:
            (ttx, tty, ttz) = left_hand.lmList[Hand.Keypoints.THUMB_TIP.value]
            (itx, ity, itz) = left_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]

            distance = math.dist((ttx, tty), (itx, ity))
            delta = 0.1 # (1-0)/10 -> (end value - init value) / num steps
            value = distance // delta

            cv2.line(frame, (ttx, tty), (itx, ity), (255, 0, 255), 2)
            cv2.putText(frame, str(value), (itx, ity), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        return frame

        # Old stuff:
        # if right_hand:
        #     # (cx, cy) = right_hand["center"]
        #     (wx, wy, wz) = right_hand.lmList[Hand.Keypoints.WRIST.value]
        #     (pmx, pmy, pmz) = right_hand.lmList[Hand.Keypoints.PINKY_MCP.value]
        #     (imx, imy, imz) = right_hand.lmList[Hand.Keypoints.INDEX_FINGER_MCP.value]
        #     (itx, ity, itz) = right_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]
        #
        #     minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy))) * 0.75
        #
        #     distance = math.dist((imx, imy), (itx, ity))
        #     angle = math.degrees(math.atan2(ity - imy, itx - imx))
        #     # print(angle)
        #     delta = 25  # max 45
        #
        #     (mtx, mty, mtz) = right_hand.lmList[Hand.Keypoints.MIDDLE_FINGER_TIP.value]
        #     (rtx, rty, rtz) = right_hand.lmList[Hand.Keypoints.RING_FINGER_TIP.value]
        #     (ptx, pty, ptz) = right_hand.lmList[Hand.Keypoints.PINKY_TIP.value]
        #     (rmx, rmy, rmz) = right_hand.lmList[Hand.Keypoints.RING_FINGER_MCP.value]
        #
        #     otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
        #                            math.dist((rtx, rty), (rmx, rmy)),
        #                            math.dist((ptx, pty), (rmx, rmy)))
        #     if otherFingersDist > minDist:
        #         return HandGesture.NONE, None
        #
        #     if distance > minDist:
        #         if (-45 + delta) < angle < (45 - delta):
        #             command = HandGesture.POINT_LEFT
        #         elif (45 + delta) < angle < (135 - delta):
        #             command = HandGesture.POINT_DOWN
        #         elif (-135 + delta) < angle < (-45 - delta):
        #             command = HandGesture.POINT_UP
        #         elif (135 + delta) < angle or angle < (-135 - delta):
        #             command = HandGesture.POINT_RIGHT
        #
        # # if command is not None and left_hand:
        # #     pass
        #
        # return command, 15
