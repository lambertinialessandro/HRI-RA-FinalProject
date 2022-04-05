
import sys

import cv2
import math
import mediapipe as mp

from modules.hand_traking.HandEnum import HandEnum

from modules.control.ControlModule import Command

sys.path.append('../../')

"""
STATIC_IMAGE_MODE:
If set to false, the solution treats the input images as a video stream. It will try to detect hands in the first input images, and upon a successful detection further localizes the hand landmarks. In subsequent images, once all max_num_hands hands are detected and the corresponding hand landmarks are localized, it simply tracks those landmarks without invoking another detection until it loses track of any of the hands. This reduces latency and is ideal for processing video frames. If set to true, hand detection runs on every input image, ideal for processing a batch of static, possibly unrelated, images. Default to false.

MAX_NUM_HANDS:
Maximum number of hands to detect. Default to 2.

MODEL_COMPLEXITY:
Complexity of the hand landmark model: 0 or 1. Landmark accuracy as well as inference latency generally go up with the model complexity. Default to 1.

MIN_DETECTION_CONFIDENCE:
Minimum confidence value ([0.0, 1.0]) from the hand detection model for the detection to be considered successful. Default to 0.5.

MIN_TRACKING_CONFIDENCE:
Minimum confidence value ([0.0, 1.0]) from the landmark-tracking model for the hand landmarks to be considered tracked successfully, or otherwise hand detection will be invoked automatically on the next input image. Setting it to a higher value can increase robustness of the solution, at the expense of a higher latency. Ignored if static_image_mode is true, where hand detection simply runs on every image. Default to 0.5.
"""


class HolisticDetector:
    def __init__(self, static_image_mode=False, model_complexity=1,
                 smooth_landmarks=True, enable_segmentation=False,
                 smooth_segmentation=True, refine_face_landmarks=False,
                 min_tracking_confidence=.5, min_detection_confidence=.5):

        self.mp_draw = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(static_image_mode=static_image_mode,
                                         model_complexity=model_complexity,
                                         smooth_landmarks=smooth_landmarks,
                                         enable_segmentation=enable_segmentation,
                                         smooth_segmentation=smooth_segmentation,
                                         refine_face_landmarks=refine_face_landmarks,
                                         min_tracking_confidence=min_tracking_confidence,
                                         min_detection_confidence=min_detection_confidence)

        self.all_hands = []
        self.results_data = False

    def analyze_frame(self, frame, flip_type=True):
        """
        Parameters
        ----------
        frame : 3-dimensional array

        flip_type : boolean, optional
            The default is True.
            flip hands lable between left and right
        Returns
        -------
        None.

        save data in allHands.
        to get this data use: getHandsInfo

        """
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

                if flip_type:
                    if handType.classification[0].label == "Right":
                        my_hand["type"] = "Left"
                    else:
                        my_hand["type"] = "Right"
                else:
                    my_hand["type"] = handType.classification[0].label
                self.all_hands.append(my_hand)

    def execute(self, frame):
        command = None

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
                return None

            if distance > minDist:
                if (-45 + delta) < angle < (45 - delta):
                    draw_command_color = (255, 0, 0) # Blue -> left
                    command = Command.ROTATE_CW
                    action = "ROTATE_CW"
                elif (45 + delta) < angle < (135 - delta):
                    draw_command_color = (0, 255, 0) # Green -> bottom
                    command = Command.LAND
                    action = "LAND"
                elif (-135 + delta) < angle < (-45 - delta):
                    draw_command_color = (0, 0, 255) # Red -> top
                    command = Command.TAKE_OFF
                    action = "MOVE_FORWARD"
                elif (135+delta) < angle or angle < (-135-delta):
                    draw_command_color = (255, 0, 255) # magenta -> right
                    command = Command.ROTATE_CCW
                    action = "ROTATE_CCW"

            cv2.line(frame, (imx, imy), (itx, ity), draw_command_color, 2)
            cv2.putText(frame, action, (itx, ity), cv2.FONT_HERSHEY_PLAIN, 2, draw_command_color, 2)

        return command

    def get_hands_info(self, hand_no=-1):
        """
        Parameters
        ----------
        hand_no : int | str, optional
            The default is -1.
            int:
                -1: return data of all hands

                N: return data of N-th hand
                    N belongs to [0, maxHands]

            str:
                "left" or "right"
        Returns
        -------
        lmList : TYPE
            DESCRIPTION.

        """
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


def main():
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        detector = HandDetector(detection_con=.8, track_con=.8)

        while True:
            success, img = cap.read()
            detector.analize_frame(img, flip_type=True)
            command = detector.execute(img)
            print(command)

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
    except:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


