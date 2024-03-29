
from enum import Enum
import time
import mediapipe as mp
import cv2

import pyttsx3
from simple_pid import PID

import sys
sys.path.append('../../')

from modules.command_recognition.model.keypoint_classifier import HandGesture
from modules.command_recognition.HandGestureModule import HandGestureRecognizer, Hand
from modules.command_recognition.FaceGestureModule import Face
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule
from modules.stream.RecordVideoModule import RecordVideoModule

from modules.control.ControlModule import Command


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


class PoseEnum(Enum):
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16


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

        self.gesture, self.value = HandGesture.NONE, 0
        self.old_gesture = Command.NONE
        self.time_g = time.time()
        self.left_hand = None
        self.right_hand = None
        self.face = None
        self.pose = None

        p = 0.7
        i = 0.
        d = 0.
        self._pid_x = PID(p, i, d, sample_time=0.01, setpoint=0.5)
        self._pid_y = PID(p, i, d, sample_time=0.01, setpoint=0.5)
        self._pid_z = PID(p, i, d, sample_time=0.01, setpoint=0.18)

        self.old_control_x = 0
        self.old_control_y = 0
        self.old_control_z = 0

        self.frame = None

    def _analyze_frame(self, frame):
        self.frame = frame
        self.left_hand = None
        self.right_hand = None
        self.face = None
        self.pose = None

        results = self.holistic_detection.process(self.frame)
        self.results = results

        if results.left_hand_landmarks:
            h, w, c = self.frame.shape

            mylm_list = []
            x_list = []
            y_list = []

            for id, lm in enumerate(results.left_hand_landmarks.landmark):
                px, py, pz = lm.x, lm.y, lm.x
                mylm_list.append([px, py, pz])
                x_list.append(px)
                y_list.append(py)

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
                px, py, pz = lm.x, lm.y, lm.x
                mylm_list.append([px, py, pz])
                x_list.append(px)
                y_list.append(py)

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
            self.face = Face(
                x=min_x,
                y=min_y,
                w=max_x-min_x,
                h=max_y-min_y,
                detection=0.0,
                keypoints=keypoints
            )

        if self.results.pose_landmarks:
            keypoints = [[lm.x, lm.y]for lm in self.results.pose_landmarks.landmark]
            self.pose = keypoints

    def follow_face(self, face):
        command = Command.SET_RC
        control_x = self._pid_x(face.center[0])
        control_y = self._pid_y(face.center[1])

        if control_x == self.old_control_x and control_y == self.old_control_y:
            return Command.NONE, None

        if control_x != self.old_control_x:
            self.old_control_x = control_x
        if control_y != self.old_control_y:
            self.old_control_y = control_y

        control_x *= -100
        control_y *= 100

        value = (0, 0, int(control_y), int(control_x))

        return command, value

    def follow_body(self, face):
        command, value = self.follow_face(face)
        control_z = self._pid_z(face.w)

        if command == Command.SET_RC:
            x = value[3]
            y = value[2]

            command = Command.SET_RC

            if control_z != self.old_control_z:
                self.old_control_z = control_z

            control_z *= 100 * 3

            value = (0, int(control_z), y, x)
            return command, value
        else:
            if control_z == self.old_control_z:
                return Command.NONE, None
            else:
                return Command.SET_RC, (0, int(control_z), 0, 0)

    def _execute(self) -> tuple:
        command = Command.NONE
        value = None
        if self.left_hand is not None and self.right_hand is not None:
            self.gesture, self.value = HandGestureRecognizer.execute(self.left_hand, self.right_hand)

            if self.gesture == HandGesture.FORWARD:
                command, value = Command.MOVE_FORWARD, self.value
            elif self.gesture == HandGesture.STOP:
                command, value = Command.NONE, self.value
            elif self.gesture == HandGesture.UP:
                command, value = Command.MOVE_UP, self.value
            elif self.gesture == HandGesture.LAND:
                command, value = Command.LAND, self.value
            elif self.gesture == HandGesture.DOWN:
                command, value = Command.MOVE_DOWN, self.value
            elif self.gesture == HandGesture.BACK:
                command, value = Command.MOVE_BACKWARD, self.value
            elif self.gesture == HandGesture.LEFT:
                command, value = Command.MOVE_LEFT, self.value
            elif self.gesture == HandGesture.RIGHT:
                command, value = Command.MOVE_RIGHT, self.value
            else:
                command, value = Command.NONE, 0

            if self.old_gesture == self.gesture:
                elapsed_t = time.time() - self.time_g
                if elapsed_t > 2:
                    self.time_g = time.time()
                else:
                    command, value = Command.NONE, value
            else:
                self.old_gesture = self.gesture
                self.time_g = time.time()
                command, value = Command.NONE, value

        if self.face is not None and self.gesture == HandGesture.NONE:
            command, value = self.follow_face(self.face)
        elif self.face is not None:
            command, value = self.follow_body(self.face)

        elapsed_t = time.time() - self.time_g
        if elapsed_t < 2:
            command, value = Command.NONE, value

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

        if self.right_hand is not None and self.left_hand is not None:
            frame = HandGestureRecognizer.edit_frame(frame,
                                                 self.left_hand, self.right_hand,
                                                 self.gesture, self.value)

        h, w, _ = frame.shape
        shape = (w, h)
        center = w//2, h//2
        if self.face is not None:
            cv2.rectangle(frame, self.face.to_unnormalized_tuple(shape), (255, 0, 255), 2)

            cv2.circle(frame, (int(self.face.x*w), int(self.face.y*h)),
                       4, (0, 255, 0), cv2.FILLED)

            cv2.circle(frame, self.face.unnormalized_center(shape),
                       2, (0, 255, 0), cv2.FILLED)

            cv2.line(frame, center, self.face.unnormalized_center(shape),
                     (0, 0, 0), thickness=1)
            cv2.line(frame, center, (
                            int(center[0] - self.old_control_x*360),
                            int(center[1] - self.old_control_y*360)
                        ), (255, 0, 0), thickness=2)

        cv2.circle(frame, center, 5, (0, 0, 255), cv2.FILLED)
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

    def _search_intruder(self):
        res, command, value = False, Command.NONE, None

        if self.face is not None:
            elapsed_t = time.time() - self.recognize_T

            command, value = self.follow_face(self.face)
            self.stopped_s = True

            if elapsed_t >= 3:
                res = True
        else:
            self.recognize_T = time.time()
            elapsed_t = time.time() - self.stopped_s
            if elapsed_t > 10:
                value = (0, 0, 0, 20)
                res, command, value = False, Command.SET_RC, value
                self.stopped_s = time.time()

        return res, command, value

    def _secret_pass(self):
        if self.pose is not None:
            ls = self.pose[PoseEnum.LEFT_SHOULDER.value]
            rs = self.pose[PoseEnum.RIGHT_SHOULDER.value]
            le = self.pose[PoseEnum.LEFT_ELBOW.value]
            re = self.pose[PoseEnum.RIGHT_ELBOW.value]
            lw = self.pose[PoseEnum.LEFT_WRIST.value]
            rw = self.pose[PoseEnum.RIGHT_WRIST.value]

            if (ls[0] > rw[0] and le[0] > rw[0]) and \
                (rs[0] < lw[0] and re[0] < lw[0]) and \
                (le[1] > rw[1] and rw[1] > ls[1]) and \
                (re[1] > lw[1] and lw[1] > rs[1]):
                    return True
        return False

    def _follow_intruder(self):
        res, command, value = False, Command.NONE, None

        if self._secret_pass():
            elapsed_T = time.time() - self.secret_T

            if elapsed_T > 1:
                res = True

        elif self.face is not None:
            command, value = super().follow_body(self.face)
            self.secret_T = time.time()

        return res, command, value

    def _execute(self) -> tuple:
        command, value = Command.NONE, None

        if self.state == 0:  # Inactive
            elapsed_t = time.time() - self.init_t
            if elapsed_t > 3:
                self.state = 1

                self.old_control_x = 0
                self.old_control_y = 0
                self.old_control_z = 0
                self.stopped_s = time.time()
                self.recognize_T = time.time()

                command, value = Command.TAKE_OFF, None
                self._talk("checking for some intrusor")

        elif self.state == 1:  # Searching
            res, command, value = self._search_intruder()
            if res:
                self._rec = RecordVideoModule(f"video_{int(time.time())}.mp4", self.frame.shape)
                self.state = 2
                self.secret_T = time.time()
                self._talk("find one intrusor, starting follow")

        elif self.state == 2:  # Following
            res, command, value = self._follow_intruder()

            self._rec.write_frame(self.frame)

            if res:
                self.state = 3

                self._rec.end()
                self._talk("recognized person")

        elif self.state == 3:  # Identified
            command, value = super()._execute()

        return command, value

    def end(self):
        super().end()

        if self._rec is not None:
            self._rec.end()
