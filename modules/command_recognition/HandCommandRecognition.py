import math
from enum import Enum
import mediapipe as mp
import cv2

# TODO
# only for debug, to be deleted
import sys

sys.path.append('../')

from modules.command_recognition.HandGestureRecognizer import HandGestureRecognizer, HandGesture, HandEnum
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule
from modules.control.ControlModule import Command


class MediaPipeHandCommandRecognition(AbstractCommandRecognitionModule):
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

        # collecting infos
        if results.multi_hand_landmarks:
            h, w, c = frame.shape
            for handType, handLms in zip(results.multi_handedness, results.multi_hand_landmarks):
                my_hand = {}
                mylm_list = []
                x_list = []
                y_list = []

                # data = handType.classification[0]
                # print("{}, {:.2f}, {}".format(data.index,
                #                              data.score,
                #                              data.label))

                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylm_list.append([px, py, pz])
                    x_list.append(px)
                    y_list.append(py)

                # bbox
                xmin, xmax = min(x_list), max(x_list)
                ymin, ymax = min(y_list), max(y_list)
                boxW = xmax - xmin
                boxH = ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx = bbox[0] + (bbox[2] // 2)
                cy = bbox[1] + (bbox[3] // 2)

                my_hand["lmList"] = mylm_list
                my_hand["bbox"] = bbox
                my_hand["center"] = (cx, cy)

                if self.flip_type:
                    if handType.classification[0].label == "Right":
                        my_hand["type"] = "Left"
                    else:
                        my_hand["type"] = "Right"
                else:
                    my_hand["type"] = handType.classification[0].label
                self.all_hands.append(my_hand)

    def _execute(self, data) -> tuple:
        r_hand = self._get_hands_info(hand_no="rx")
        l_hand = self._get_hands_info(hand_no="lx")

        gesture, value = HandGestureRecognizer.execute(l_hand, r_hand)

        if gesture == HandGesture.POINT_RIGHT:
            return Command.MOVE_UP, value  # TODO
        elif gesture == HandGesture.POINT_LEFT:
            return Command.MOVE_UP, value  # TODO
        elif gesture == HandGesture.POINT_UP:
            return Command.MOVE_UP, value  # TODO
        elif gesture == HandGesture.POINT_DOWN:
            return Command.MOVE_UP, value  # TODO
        else:
            return Command.NONE, value

    def edit_frame(self, frame):
        for hand in self.all_hands:
            bbox = hand["bbox"]
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        r_hand = self._get_hands_info(hand_no="rx")
        if r_hand:
            (wx, wy, wz) = r_hand["lmList"][HandEnum.WRIST.value]
            (pmx, pmy, pmz) = r_hand["lmList"][HandEnum.PINKY_MCP.value]
            (imx, imy, imz) = r_hand["lmList"][HandEnum.INDEX_FINGER_MCP.value]
            (itx, ity, itz) = r_hand["lmList"][HandEnum.INDEX_FINGER_TIP.value]

            minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy)))*0.75

            distance = math.dist((imx, imy), (itx, ity))
            angle = math.degrees(math.atan2(ity-imy, itx-imx))
            #print(angle)
            draw_command_color = (0, 0, 0)
            delta = 25  # max 45
            action = ""

            (mtx, mty, mtz) = r_hand["lmList"][HandEnum.MIDDLE_FINGER_TIP.value]
            (rtx, rty, rtz) = r_hand["lmList"][HandEnum.RING_FINGER_TIP.value]
            (ptx, pty, ptz) = r_hand["lmList"][HandEnum.PINKY_TIP.value]
            (rmx, rmy, rmz) = r_hand["lmList"][HandEnum.RING_FINGER_MCP.value]

            otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
                                   math.dist((rtx, rty), (rmx, rmy)),
                                   math.dist((ptx, pty), (rmx, rmy)))
            if otherFingersDist > minDist:
                return frame

            if distance > minDist:
                if (-45 + delta) < angle < (45 - delta):
                    draw_command_color = (255, 0, 0) # Blue -> left
                    action = "ROTATE_CW"
                elif (45 + delta) < angle < (135 - delta):
                    draw_command_color = (0, 255, 0) # Green -> bottom
                    action = "LAND"
                elif (-135 + delta) < angle < (-45 - delta):
                    draw_command_color = (0, 0, 255) # Red -> top
                    action = "MOVE_FORWARD"
                elif (135+delta) < angle or angle < (-135-delta):
                    draw_command_color = (255, 0, 255) # magenta -> right
                    action = "ROTATE_CCW"

            cv2.line(frame, (imx, imy), (itx, ity), draw_command_color, 2)
            cv2.putText(frame, action, (itx, ity), cv2.FONT_HERSHEY_PLAIN, 2, draw_command_color, 2)

        return frame

    def _get_hands_info(self, hand_no):
        if isinstance(hand_no, str):
            if hand_no.lower() == "lx":
                for hand in self.all_hands:
                    if hand["type"].lower() == "lx":
                        return hand
            elif hand_no.lower() == "rx":
                for hand in self.all_hands:
                    if hand["type"].lower() == "rx":
                        return hand
        else:
            raise ValueError(hand_no)

        return []

    def end(self):
        pass
