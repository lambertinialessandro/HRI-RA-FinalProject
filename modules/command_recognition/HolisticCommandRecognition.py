
import time
import mediapipe as mp
import cv2
import pyttsx3

import sys
sys.path.append('../../')

from modules.command_recognition.HandCommandRecognition import Hand
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

        self.results = None

    def _analyze_frame(self, frame):
        results = self.holistic_detection.process(frame)
        self.results = results

        if results.left_hand_landmarks:
            h, w, c = frame.shape

            mylm_list = []
            x_list = []
            y_list = []

            for id, lm in enumerate(results.left_hand_landmarks.landmark):
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

            hand = Hand(
                center=(cx, cy),
                bbox=bbox,
                lmList=mylm_list,
                type=Hand.HandType.LEFT
            )
            self.left_hand = hand

        if results.right_hand_landmarks:
            h, w, c = frame.shape

            mylm_list = []
            x_list = []
            y_list = []

            for id, lm in enumerate(results.right_hand_landmarks.landmark):
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

            hand = Hand(
                center=(cx, cy),
                bbox=bbox,
                lmList=mylm_list,
                type=Hand.HandType.RIGHT
            )
            self.right_hand = hand



        return self.holistic_detection.process(frame)

    def _execute(self) -> tuple:
        command = Command.NONE, None
        # TODO
        return command

    def edit_frame(self, frame):
        if self.results is None:
            return frame

        mp_drawing.draw_landmarks(
            frame,
            self.results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        mp_drawing.draw_landmarks(
            frame,
            self.results.left_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        mp_drawing.draw_landmarks(
            frame,
            self.results.right_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        # mp_drawing.draw_landmarks(
        #     frame,
        #     self.results.face_landmarks,
        #     mp_holistic.FACEMESH_CONTOURS,
        #     landmark_drawing_spec=mp_drawing_styles
        #     .get_default_pose_landmarks_style())

        return frame

    def end(self):
        pass


class HolisticRACommandRecognition(HolisticCommandRecognition):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.engine = pyttsx3.init()

        self.state = 0
        self.init_t = time.time()
        self._talk("Starting Controll procedure")

    def _talk(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def f_state_2(self):
        res, command, value = False, Command.NONE, None

        if self.results.face_landmarks:
            elapsed_t = time.time() - self.recognize_T

            command, value = self.follow_face()

            if elapsed_t >= 3:
                res = True
        else:
            self.recognize_T = time.time()
            res, command, value = False, Command.ROTATE_CW, 30

        return res, command, value

    def _execute(self) -> tuple:
        command, value = Command.NONE, None

        if self.state == 0:  # Inactive
            elapsed_t = time.time() - self.init_t
            if elapsed_t > 3:
                self.state = 1
                command, value = Command.TAKE_OFF, None
                self._talk("checking for some intrusor")

        elif self.state == 1:  # Searching
            res, command, value = self.f_state_2()
            if res:
                self.state = 2
                self._talk("find one intrusor, starting follow")

        elif self.state == 2:  # Following
            # TODO follow as in face
            res, command, value = self.f_state_3()

            if res:
                pass

            if False:
                self.state = 3
                self._talk("recognized person")

        elif self.state == 3:  # Identified
            command, value = super()._execute()

        return command, value
