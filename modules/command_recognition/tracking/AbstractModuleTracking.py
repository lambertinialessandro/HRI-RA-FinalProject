from abc import ABC, abstractmethod


class AbstractModuleTracking(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def analyze_frame(self, frame):
        pass

    @abstractmethod
    def execute(self, results) -> tuple:
        pass

    # def execute(self, frame) -> tuple:
    #     results = self.analyze_frame(frame)
    #     return self._execute(results)

    @abstractmethod
    def edit(frame):
        pass


class EmptyTracking(AbstractModuleTracking):
    @classmethod
    def analyze_frame(cls, frame):
        return []

    @classmethod
    def execute(cls, frame) -> tuple:
        return None, None

    # def execute(self, frame) -> tuple:
    #     return None, None

    @abstractmethod
    def edit(frame):
        return frame
