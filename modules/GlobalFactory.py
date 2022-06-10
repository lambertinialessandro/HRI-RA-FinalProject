
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.drone.DroneFactory import DroneFactory, DroneEnum

from modules.stream.StreamFactory import StreamFactory, StreamEnum
from modules.command_recognition.CommandRecognitionFactory import \
    VideoCommandRecognitionFactory, VCREnum
from modules.reasoning_agent.ReasoningAgentModule import ReasoningAgent
from modules.control import ControlModule
from modules.template_pattern.TemplatePatternFactory import \
    TemplatePatternFactory, TemplateEnum



class GlobalFactory:
    DroneEnum = DroneEnum
    StreamEnum = StreamEnum
    VCREnum = VCREnum
    TemplateEnum = TemplateEnum

    def __init__(self):
        pass

    @staticmethod
    def create(type_drone: DroneEnum,
               type_stream: StreamEnum,
               type_cr: VCREnum,
               type_template: TemplateEnum,
               input_idx=0, capture_api=None):

        drone, drone_edit_frame = DroneFactory.create(type_drone,
                                                      input_idx=input_idx,
                                                      capture_api=capture_api)

        stream_module = StreamFactory.create(type_stream,
                                             drone=drone)

        command_recognition = VideoCommandRecognitionFactory.create(type_cr)

        control_module = ControlModule.ControlModule(drone)

        template_pattern = TemplatePatternFactory.create(type_template,
                                                         drone,
                                                         stream_module,
                                                         command_recognition,
                                                         control_module,
                                                         drone_edit_frame)

        return template_pattern


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    input_idx = 0
    if platform.system() == 'Windows':
        capture_api = cv2.CAP_DSHOW
        input_idx = 1

    templatye_pattern = GlobalFactory.create(GlobalFactory.DroneEnum.FakeDrone,
                                            GlobalFactory.StreamEnum.VideoDrone,
                                            input_idx=input_idx, capture_api=capture_api)

    templatye_pattern.execute()
