from abc import ABC, abstractmethod


class AbstractCommandRecognitionModule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _analyze_frame(self, frame):
        pass

    @abstractmethod
    def _execute(self) -> tuple:  # Command, value
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

import sys
sys.path.append('../../')
from modules.control.ControlModule import Command

class EmptyCommandRecognition(AbstractCommandRecognitionModule):
    def __init__(self):
        super().__init__()

    def _analyze_frame(self, frame):
        pass

    def _execute(self) -> tuple:  # Command, value
        return Command.NONE, None

    def edit_frame(self, frame):
        return frame

    def end(self):
        pass
