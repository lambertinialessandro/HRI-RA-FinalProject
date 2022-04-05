
import cv2
import math
from enum import Enum
import mediapipe as mp

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../../')

from modules.command_recognition.tracking.AbstractModuleTracking import AbstractModuleTracking

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command


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


class AbstractHandTracking(AbstractModuleTracking):
    def __init__(self, flip_type=True):
        self.flip_type = flip_type

    def _analyze_frame(self, frame):
        self.all_hands = []

        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.results_data = False

        # collecting infos
        if results.multi_hand_landmarks:
            self.results_data = True
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


class HandTracking(AbstractHandTracking):
    def __init__(self, mode=False, max_hands=2, detection_con=.5, track_con=.5, flip_type=True):
        super().__init__(flip_type=flip_type)
        self.mode = mode  # STATIC_IMAGE_MODE
        self.max_hands = max_hands  # MAX_NUM_HANDS
        self.detection_con = detection_con  # MIN_DETECTION_CONFIDENCE
        self.track_con = track_con  # MIN_TRACKING_CONFIDENCE

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=self.mode,
                                         max_num_hands=self.max_hands,
                                         min_detection_confidence=self.detection_con,
                                         min_tracking_confidence=self.track_con)

        self.all_hands = []
        self.results_data = False

    def execute(self, frame):
        command = Command.NONE, None

        self._analyze_frame(frame)

        for hand in self.all_hands:
            bbox = hand["bbox"]
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        r_hand = self.get_hands_info(hand_no="Right")
        if r_hand:
            # (cx, cy) = r_hand["center"]
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
                return Command.NONE, None

            if distance > minDist:
                if (-45 + delta) < angle < (45 - delta):
                    draw_command_color = (255, 0, 0) # Blue -> left
                    command = Command.ROTATE_CW, 15
                    action = "ROTATE_CW"
                elif (45 + delta) < angle < (135 - delta):
                    draw_command_color = (0, 255, 0) # Green -> bottom
                    command = Command.LAND, None
                    action = "LAND"
                elif (-135 + delta) < angle < (-45 - delta):
                    draw_command_color = (0, 0, 255) # Red -> top
                    command = Command.TAKE_OFF, None
                    action = "MOVE_FORWARD"
                elif (135+delta) < angle or angle < (-135-delta):
                    draw_command_color = (255, 0, 255) # magenta -> right
                    command = Command.ROTATE_CCW, 15
                    action = "ROTATE_CCW"

            cv2.line(frame, (imx, imy), (itx, ity), draw_command_color, 2)
            cv2.putText(frame, action, (itx, ity), cv2.FONT_HERSHEY_PLAIN, 2, draw_command_color, 2)

        return command

    def get_hands_info(self, hand_no=-1):
        if isinstance(hand_no, int):
            assert hand_no < self.max_hands

            if hand_no < 0:
                return self.all_hands
            else:
                if hand_no <= len(self.all_hands):
                    return self.all_hands[hand_no]
        elif isinstance(hand_no, str):
            if hand_no.lower() == "left":
                for hand in self.all_hands:
                    if hand["type"].lower() == "left":
                        return hand
            elif hand_no.lower() == "right":
                for hand in self.all_hands:
                    if hand["type"].lower() == "right":
                        return hand
        return []


# TODO
# only for debug, to be deleted
def main():
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        detector = HandTracking(detection_con=.8, track_con=.8, flip_type=True)

        while True:
            success, img = cap.read()
            command = detector.execute(img)
            print(command)

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


