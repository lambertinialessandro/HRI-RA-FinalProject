from abc import ABC, abstractmethod


class AbstractModuleTracking(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def _analyze_frame(cls, frame):
        pass

    @classmethod
    @abstractmethod
    def execute(cls, frame) -> tuple:
        pass


class EmptyTracking(AbstractModuleTracking):
    def _analyze_frame(self, frame):
        return

    def execute(self, frame) -> tuple:
        return None, None
