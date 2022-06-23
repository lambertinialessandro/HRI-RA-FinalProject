import copy
import itertools

import tensorflow as tf
import numpy as np


class KeyPointClassifier(object):
    def __init__(
        self,
        model_path='modules/command_recognition/model/keypoint_classifier.tflite',
    ):
        self.interpreter = tf.lite.Interpreter(
            model_path=model_path,
            num_threads=1
        ).allocate_tensors()

        self.input = self.interpreter.get_input_details()
        self.output = self.interpreter.get_output_details()

    def classify(self, landmarks):
        landmarks = np.array([self._pre_process_landmark(landmarks)], dtype=np.float32)

        input_details_tensor_index = self.input[0]['index']
        self.interpreter.set_tensor(
            input_details_tensor_index,
            landmarks,
        )
        self.interpreter.invoke()

        output_index = self.output[0]['index']

        result = np.argmax(
            np.squeeze(
                self.interpreter.get_tensor(output_index)
            )
        )

        return result

    def _pre_process_landmark(self, landmarks):
        temp_landmarks = copy.deepcopy(landmarks)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmarks):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmarks[index][0] = temp_landmarks[index][0] - base_x
            temp_landmarks[index][1] = temp_landmarks[index][1] - base_y
            temp_landmarks[index].pop()

        # Convert to a one-dimensional list
        temp_landmarks = list(itertools.chain.from_iterable(temp_landmarks))

        # Normalization
        max_value = max(list(map(abs, temp_landmarks)))

        temp_landmarks = list(map(lambda n: n / max_value, temp_landmarks))

        return temp_landmarks
