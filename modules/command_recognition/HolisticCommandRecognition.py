import math
from abc import abstractmethod
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


class AbstractHolisticCommandRecognition(AbstractCommandRecognitionModule):
    def __init__(self, static_image_mode=False, model_complexity=1,
                 smooth_landmarks=True, enable_segmentation=False,
                 smooth_segmentation=True, refine_face_landmarks=True,
                 min_tracking_confidence=.5, min_detection_confidence=.5,
                 flip_type=True):
        super().__init__()
        self.flip_type = flip_type

        self.mp_holistic = mp.solutions.holistic
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
        self.all_hands = []
        self.results_data = False

    def _analyze_frame(self, frame):
        self.all_hands = []

        results = self.holistic_detection.process(frame)

        # result: 'pose_landmarks', 'pose_world_landmarks', 'left_hand_landmarks',
        #         'right_hand_landmarks', 'face_landmarks', 'segmentation_mask'

        # mp_holistic: 'FACEMESH_CONTOURS', 'FACEMESH_TESSELATION',
        #              'HAND_CONNECTIONS', 'POSE_CONNECTIONS'

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        mp_drawing.draw_landmarks(
            frame,
            results.left_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        mp_drawing.draw_landmarks(
            frame,
            results.right_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        # mp_drawing.draw_landmarks(
        #     frame,
        #     results.face_landmarks,
        #     mp_holistic.FACEMESH_CONTOURS,
        #     landmark_drawing_spec=mp_drawing_styles
        #     .get_default_pose_landmarks_style())

    @abstractmethod
    def _execute(self) -> tuple:
        pass

    @abstractmethod
    def edit_frame(self, frame):
        pass

    def end(self):
        pass


class HolisticCommandRecognition(AbstractHolisticCommandRecognition):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def _execute(self) -> tuple:
        command = Command.NONE, None

        r_hand = self._get_hands_info(hand_no="Right")
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
            delta = 25  # max 45

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
                    command = Command.ROTATE_CW, 15 # Blue -> left
                elif (45 + delta) < angle < (135 - delta):
                    command = Command.LAND, None # Green -> bottom
                elif (-135 + delta) < angle < (-45 - delta):
                    command = Command.TAKE_OFF, None # Red -> top
                elif (135+delta) < angle or angle < (-135-delta):
                    command = Command.ROTATE_CCW, 15 # magenta -> right

        return command

    def edit_frame(self, frame):
        for hand in self.all_hands:
            bbox = hand["bbox"]
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20),
                          (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                          (255, 0, 255), 2)
            cv2.putText(frame, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 0, 255), 2)

        r_hand = self._get_hands_info(hand_no="Right")
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

    def _get_hands_info(self, hand_no=-1):
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


import time
class HolisticRACommandRecognition(HolisticCommandRecognition):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.state = 0
        self.init_t = time.time()

    def _execute(self) -> tuple:
        command = Command.NONE, None

        if self.state == 0: # Inactive
            elapsed_t = time.time() - self.init_t
            if elapsed_t > 3:
                self.state = 1
                command = Command.TAKE_OFF, None

        elif self.state == 1: # Searching
            if self.all_hands:
                # TODO : if resoults for 2 seconds
                self.state = 2
            else:
                command = Command.ROTATE_CW, 30

        elif self.state == 2: # Following
            pass # TODO follow as in face

        elif self.state == 3: # Identified
            command = super()._execute()

        return command



def main():
    #try:
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        #cap.set(3, 1280//2)
        #cap.set(4, 720//2)
        detector = HolisticCommandRecognition(min_detection_confidence=.8, min_tracking_confidence=.8)

        while True:
            success, img = cap.read()
            detector._analyze_frame(img)
            #command = detector.execute(img)
            #print(command)

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
    #except:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


