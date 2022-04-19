from abc import ABC, abstractmethod


class AbstractModuleTracking(ABC):
    def __init__(cls):
        pass

    @abstractmethod
    def _analyze_frame(cls, frame):
        pass

    @abstractmethod
    def _execute(cls) -> tuple:
        pass

    def execute(cls, frame) -> tuple:
        cls._analyze_frame(frame)
        return cls._execute()

    @abstractmethod
    def edit_frame(cls, frame):
        pass

    @abstractmethod
    def end(cls):
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
