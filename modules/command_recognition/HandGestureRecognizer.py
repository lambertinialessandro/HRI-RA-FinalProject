import dataclasses
from enum import Enum
import math


class HandGestureRecognizer:
    @staticmethod
    def execute(left_hand, right_hand) -> tuple:  # Gesture, value
        command = None

        if right_hand:
            # (cx, cy) = right_hand["center"]
            (wx, wy, wz) = right_hand.lmList[HandEnum.WRIST.value]
            (pmx, pmy, pmz) = right_hand.lmList[HandEnum.PINKY_MCP.value]
            (imx, imy, imz) = right_hand.lmList[HandEnum.INDEX_FINGER_MCP.value]
            (itx, ity, itz) = right_hand.lmList[HandEnum.INDEX_FINGER_TIP.value]

            minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy))) * 0.75

            distance = math.dist((imx, imy), (itx, ity))
            angle = math.degrees(math.atan2(ity - imy, itx - imx))
            # print(angle)
            delta = 25  # max 45

            (mtx, mty, mtz) = right_hand.lmList[HandEnum.MIDDLE_FINGER_TIP.value]
            (rtx, rty, rtz) = right_hand.lmList[HandEnum.RING_FINGER_TIP.value]
            (ptx, pty, ptz) = right_hand.lmList[HandEnum.PINKY_TIP.value]
            (rmx, rmy, rmz) = right_hand.lmList[HandEnum.RING_FINGER_MCP.value]

            otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
                                   math.dist((rtx, rty), (rmx, rmy)),
                                   math.dist((ptx, pty), (rmx, rmy)))
            if otherFingersDist > minDist:
                return HandGesture.NONE, None

            if distance > minDist:
                if (-45 + delta) < angle < (45 - delta):
                    command = HandGesture.POINT_LEFT
                elif (45 + delta) < angle < (135 - delta):
                    command = HandGesture.POINT_DOWN
                elif (-135 + delta) < angle < (-45 - delta):
                    command = HandGesture.POINT_UP
                elif (135 + delta) < angle or angle < (-135 - delta):
                    command = HandGesture.POINT_RIGHT

        # if command is not None and left_hand:
        #     pass

        return command, 15


@dataclasses.dataclass
class Hand:
    class HandType(Enum):
        LEFT = "left"
        RIGHT = "right"

    center: tuple
    bbox: tuple
    lmList: list
    type: HandType


class HandGesture(Enum):
    NONE = 0
    POINT_RIGHT = 1
    POINT_LEFT = 2
    POINT_UP = 3
    POINT_DOWN = 4


class HandEnum(Enum):
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
