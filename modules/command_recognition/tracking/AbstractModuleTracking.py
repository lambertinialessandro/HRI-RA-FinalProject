from abc import ABC, abstractmethod


class AbstractModuleTracking(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _analyze_frame(self, frame):
        pass

    @abstractmethod
    def _execute(self, results):
        pass

    def execute(self, frame) -> tuple:
        results = self._analyze_frame(frame)
        return self._execute(results)


class EmptyTracking(AbstractModuleTracking):
    @classmethod
    def _analyze_frame(cls, frame):
        return

    @classmethod
    def _execute(cls, frame):
        return

    def execute(self, frame) -> tuple:
        return None, None
