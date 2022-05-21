from abc import ABC, abstractmethod


class AbstractCommandRecognitionModule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _analyze_frame(self, frame):
        pass

    @abstractmethod
    def _execute(self) -> tuple:
        pass

    def execute(self, frame) -> tuple:
        self._analyze_frame(frame)
        return self._execute()

    @abstractmethod
    def edit_frame(self, frame):
        pass

    @abstractmethod
    def end(self):
        pass
