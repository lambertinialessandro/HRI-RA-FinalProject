
from abc import ABC, abstractmethod

class AbstractModuleTracking(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def _analyze_frame(self, frame):
        pass

    @classmethod
    @abstractmethod
    def execute(self, frame) -> tuple:
        pass