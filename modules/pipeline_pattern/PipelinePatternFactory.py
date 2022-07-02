
from enum import Enum

import sys
sys.path.append('../')

from modules.reasoning_agent.ReasoningAgentModule import ReasoningAgent
from modules.pipeline_pattern.PipelinePatternModule import PipelinePattern, ReasoningPipelinePattern


class PipelineEnum(Enum):
    BasePipeline = "BasePipeline"
    ReasoningPipeline = "ReasoningPipeline"

class PipelinePatternFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(type_pipeline: PipelineEnum, drone, *args, **kwargs):
        pipeline = None

        if type_pipeline == PipelineEnum.BasePipeline:
            pipeline = PipelinePattern(drone, *args, **kwargs)
        elif type_pipeline == PipelineEnum.ReasoningPipeline:
            reasoning_agent = ReasoningAgent(drone)
            pipeline = ReasoningPipelinePattern(reasoning_agent, drone,
                                                *args, **kwargs)
        else:
            raise ValueError(f"Type pipeline '{type_pipeline}' not accepted")

        return pipeline


