
import time
import mediapipe as mp
import cv2

import pyttsx3
from simple_pid import PID

import sys
sys.path.append('../../')

from modules.command_recognition.HandGestureModule import HandGestureRecognizer, HandGesture, Hand
from modules.command_recognition.FaceGestureModule import Face
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule
from modules.stream.RecordVideoModule import RecordVideoModule

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

        self.left_hand = None
        self.right_hand = None
        self.face = None

        p = 0.7
        i = 0.  # 0.01
        d = 0.  # 0.05
        self._pid_x = PID(p, i, d, sample_time=0.01, setpoint=0.5)
        self._pid_y = PID(p, i, d, sample_time=0.01, setpoint=0.5)
        self._pid_z = PID(p, i, d, sample_time=0.01, setpoint=0.2) # TODO

        self.old_control_x = 0
        self.old_control_y = 0
        self.old_control_z = 0

        self.frame = None

    def _analyze_frame(self, frame):
        self.frame = frame
        self.left_hand = None
        self.right_hand = None
        self.face = None

        results = self.holistic_detection.process(self.frame)
        self.results = results

        if results.left_hand_landmarks:
            h, w, c = self.frame.shape

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
            h, w, c = self.frame.shape

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

        if self.results.face_landmarks:
            x_v = [p.x for p in self.results.face_landmarks.landmark]
            min_x = min(x_v)
            max_x = max(x_v)
            y_v = [p.y for p in self.results.face_landmarks.landmark]
            min_y = min(y_v)
            max_y = max(y_v)

            keypoints = [[lm.x, lm.y]for lm in self.results.face_landmarks.landmark]
            self.face = Face(x=min_x,
                            y=min_y,
                            w=max_x-min_x,
                            h=max_y-min_y,
                            detection=0.0,
                            keypoints=keypoints)

    def follow_face(self, face):
        command = Command.SET_RC
        control_x = self._pid_x(face.center[0])
        control_y = self._pid_y(face.center[1])
        control_z = self._pid_z(face.w)

        if control_x == self.old_control_x and \
                control_y == self.old_control_y and \
                control_z == self.old_control_z:
            return Command.NONE, None

        if control_x != self.old_control_x:
            self.old_control_x = control_x
        if control_y != self.old_control_y:
            self.old_control_y = control_y
        if control_z != self.old_control_z:
            self.old_control_z = control_z

        control_x *= -100
        control_y *= 100
        control_z *= 100

        control_z = control_z*1.2 if 0.1 < face.w < 0.3 else 0

        value = (0, int(control_z), int(control_y), int(control_x))
        if value == (0, 0, 0, 0):
            command = Command.NONE
            value = None
        return command, value

    def _execute(self) -> tuple:
        command = Command.NONE
        value = None
        if self.left_hand is not None and self.right_hand is not None:
            gesture, value = HandGestureRecognizer.execute(self.left_hand, self.right_hand)

            if gesture == HandGesture.POINT_RIGHT:
                return Command.MOVE_UP, value  # TODO
            elif gesture == HandGesture.POINT_LEFT:
                return Command.MOVE_UP, value  # TODO
            elif gesture == HandGesture.POINT_UP:
                return Command.MOVE_UP, value  # TODO
            elif gesture == HandGesture.POINT_DOWN:
                return Command.MOVE_UP, value  # TODO
            # elif none continue with face

        if self.face is not None:
            command, value = self.follow_face(self.face)

        return command, value

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

        mp_drawing.draw_landmarks(
            frame,
            self.results.face_landmarks,
            mp_holistic.FACEMESH_CONTOURS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())

        return frame

    def end(self):
        pass


class HolisticRACommandRecognition(HolisticCommandRecognition):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.engine = pyttsx3.init()

        self.state = 0
        self.init_t = time.time()
        self._talk("Starting control procedure")

        self._rec = None

    def _talk(self, text):
        print(text)
        self.engine.say(text)
        #self.engine.runAndWait()

    def _search_intruder(self):
        res, command, value = False, Command.NONE, None

        if self.face is not None:
            elapsed_t = time.time() - self.recognize_T

            command, value = self.follow_face(self.face)

            if elapsed_t >= 10:
                res = True
        else:
            self.recognize_T = time.time()
            value = (0, 0, 0, 3)  # self.eval_rotation()
            res, command, value = False, Command.SET_RC, value

        return res, command, value

    def _follow_intruder(self):
        res, command, value = False, Command.NONE, None

        if self.face is not None:
            command, value = super().follow_face(self.face)

        return res, command, value

    def _execute(self) -> tuple:
        command, value = Command.NONE, None

        if self.state == 0:  # Inactive
            elapsed_t = time.time() - self.init_t
            if elapsed_t > 3:
                self.state = 1

                self.old_control_x = 0
                self.old_control_y = 0
                self.recognize_T = time.time()

                command, value = Command.TAKE_OFF, None
                self._talk("checking for some intrusor")

        elif self.state == 1:  # Searching
            res, command, value = self._search_intruder()
            if res:
                self._rec = RecordVideoModule(f"video_{int(time.time())}.mp4", self.frame.shape)
                self.state = 2
                self._talk("find one intruder, starting follow")

        elif self.state == 2:  # Following
            # TODO follow as in face
            res, command, value = self._follow_intruder()

            self._rec.write_frame(self.frame)

            if res:
                pass

            if res == 3:
                self.state = 3

                self._rec.end()
                self._talk("recognized person")

        elif self.state == 3:  # Identified
            command, value = super()._execute()

        return command, value
