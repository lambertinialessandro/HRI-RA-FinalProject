from abc import ABC, abstractmethod


class AbstractModuleTracking(ABC):
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


class EmptyTracking(AbstractModuleTracking):

    def _analyze_frame(self, frame):
        return []

    def _execute(self) -> tuple:
        return None, None

    def edit_frame(self, frame):
        return frame

    def end(self):
        pass
