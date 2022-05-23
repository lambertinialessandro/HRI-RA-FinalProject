
from enum import Enum

import sys
sys.path.append('../')

from modules.reasoning_agent.ReasoningAgentModule import ReasoningAgent
from modules.template_pattern.TemplatePatternModule import TemplatePattern, ReasoningTemplatePattern


class TemplateEnum(Enum):
    BaseTemplate = "BaseTemplate"
    ReasoningTemplate = "ReasoningTemplate"

class TemplatePatternFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(type_template: TemplateEnum, drone, *args, **kwargs):
        template = None

        if type_template == TemplateEnum.BaseTemplate:
            template = TemplatePattern(drone, *args, **kwargs)
        elif type_template == TemplateEnum.ReasoningTemplate:
            reasoning_agent = ReasoningAgent(drone)
            template = ReasoningTemplatePattern(reasoning_agent, drone,
                                                *args, **kwargs)
        else:
            raise ValueError(f"Type template '{type_template}' not accepted")

        return template


