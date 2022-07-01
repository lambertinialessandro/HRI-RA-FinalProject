
import math
from abc import abstractmethod
import mediapipe as mp
import cv2
import time

# TODO
# only for debug, to be deleted
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

        # collecting infos
        if results.multi_hand_landmarks:
            h, w, c = frame.shape
            for handType, handLms in zip(results.multi_handedness, results.multi_hand_landmarks):
                mylm_list = []
                x_list = []
                y_list = []

                # data = handType.classification[0]
                # print("{}, {:.2f}, {}".format(data.index,
                #                              data.score,
                #                              data.label))

                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = lm.x, lm.y, lm.x # int(lm.x * w), int(lm.y * h), int(lm.z * w)
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
        r_hand = self._get_hands_info(Hand.HandType.RIGHT)
        l_hand = self._get_hands_info(Hand.HandType.LEFT)

        self.gesture, self.value = HandGestureRecognizer.execute(l_hand, r_hand)

        if self.gesture == HandGesture.FORWARD:
            command, value = Command.MOVE_FORWARD, self.value  # TODO
        elif self.gesture == HandGesture.STOP:
            command, value = Command.NONE, self.value  # TODO
        elif self.gesture == HandGesture.UP:
            command, value = Command.MOVE_UP, self.value  # TODO
        elif self.gesture == HandGesture.LAND:
            command, value = Command.LAND, self.value  # TODO
        elif self.gesture == HandGesture.DOWN:
            command, value = Command.MOVE_DOWN, self.value  # TODO
        elif self.gesture == HandGesture.BACK:
            command, value = Command.MOVE_BACKWARD, self.value  # TODO
        elif self.gesture == HandGesture.LEFT:
            command, value = Command.MOVE_LEFT, self.value  # TODO
        elif self.gesture == HandGesture.RIGHT:
            command, value = Command.MOVE_RIGHT, self.value  # TODO
        else:
            return Command.NONE, 0

        if self.old_gesture == self.gesture:
            elapsed_t = time.time() - self.time_g
            if elapsed_t > 2:
                self.time_g = time.time()
                return command, value
        else:
            self.old_gesture = self.gesture
            self.time_g = time.time()

        return Command.NONE, value

    def edit_frame(self, frame):
        r_hand = self._get_hands_info(Hand.HandType.RIGHT)
        l_hand = self._get_hands_info(Hand.HandType.LEFT)
        frame = HandGestureRecognizer.edit_frame(frame, l_hand, r_hand,
                                                 self.gesture, self.value)

        return frame

        for hand in self.all_hands:
            bbox = hand.bbox
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, hand.type.value, (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        if r_hand:
            (wx, wy, wz) = r_hand.lmList[Hand.Keypoints.WRIST.value]
            (pmx, pmy, pmz) = r_hand.lmList[Hand.Keypoints.PINKY_MCP.value]
            (imx, imy, imz) = r_hand.lmList[Hand.Keypoints.INDEX_FINGER_MCP.value]
            (itx, ity, itz) = r_hand.lmList[Hand.Keypoints.INDEX_FINGER_TIP.value]

            minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy)))*0.75

            distance = math.dist((imx, imy), (itx, ity))
            angle = math.degrees(math.atan2(ity-imy, itx-imx))
            #print(angle)
            draw_command_color = (0, 0, 0)
            delta = 25  # max 45
            action = ""

            (mtx, mty, mtz) = r_hand.lmList[Hand.Keypoints.MIDDLE_FINGER_TIP.value]
            (rtx, rty, rtz) = r_hand.lmList[Hand.Keypoints.RING_FINGER_TIP.value]
            (ptx, pty, ptz) = r_hand.lmList[Hand.Keypoints.PINKY_TIP.value]
            (rmx, rmy, rmz) = r_hand.lmList[Hand.Keypoints.RING_FINGER_MCP.value]

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

    def _get_hands_info(self, t: Hand.HandType):
        if t == Hand.HandType.LEFT or t == Hand.HandType.RIGHT:
            for hand in self.all_hands:
                if hand.type == t:
                    return hand
        else:
            raise ValueError(t)

    def end(self):
        pass
