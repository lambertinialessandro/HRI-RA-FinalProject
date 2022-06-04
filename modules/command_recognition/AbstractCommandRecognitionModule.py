from abc import ABC, abstractmethod


class AbstractCommandRecognitionModule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _analyze_frame(self, frame) -> tuple:  # Detector's output
        pass

    @abstractmethod
    def _execute(self, data) -> tuple:  # Command, value
        pass

    def execute(self, frame) -> tuple:
        data = self._analyze_frame(frame)
        return self._execute(data)

    @abstractmethod
    def edit_frame(self, frame):
        pass

    @abstractmethod
    def end(self):
        pass
