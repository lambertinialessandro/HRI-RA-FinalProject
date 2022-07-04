
import dataclasses
import numpy as np


@dataclasses.dataclass
class Face:
    x: float
    y: float
    w: float
    h: float
    detection: float
    keypoints: list

    @property
    def center(self) -> tuple:
        return self.x + self.w / 2, self.y + self.h / 2

    def unnormalized_center(self, shape) -> tuple:
        normalized_center = self.center
        return int(normalized_center[0] * shape[0]), int(normalized_center[1] * shape[1])

    def to_tuple(self) -> tuple:
        return self.x, self.y, self.w, self.h

    def to_unnormalized_tuple(self, shape) -> tuple:
        return int(self.x * shape[0]), int(self.y * shape[1]), \
            int(self.w * shape[0]), int(self.h * shape[1]),

    def normalize(self, width, height):
        self.x /= width
        self.w /= width

        self.y /= height
        self.h /= height

    def get_ratio(self):
        eyes = np.diff([self.keypoints[0], self.keypoints[1]])
        ears = np.diff([self.keypoints[4], self.keypoints[5]])
        return np.mean(eyes/ears)

    def unnormalized_keypoints(self, shape):
        return [[int(lm[0] * shape[0]), int(lm[1] * shape[1])] for lm in self.keypoints]
