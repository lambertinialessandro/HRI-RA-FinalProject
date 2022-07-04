
from abc import ABC, abstractmethod
import threading
import cv2

from modules.control.ControlModule import Command
from modules.window.Window import Window
from modules.pipeline_pattern.WebServer import WebServer


class AbstractPipelinePattern(ABC):
    def __init__(self, stream_module, command_recognition,
                 control_module, drone_edit_frame):
        self.stream_module = stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module
        self.drone_edit_frame = drone_edit_frame
        self.displayer = Window(binded_obj=self)

        self.mutex = threading.Lock()

    @classmethod
    @abstractmethod
    def execute(cls):
        pass

    @classmethod
    @abstractmethod
    def end(cls):
        pass


class AbstractWebServerPipelinePattern(AbstractPipelinePattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = None
        self.ip = "0.0.0.0"
        self.port = 8080
        self.lock = threading.Lock()
        self.web_server = WebServer(self._generate_frame, self.ip, self.port)

    def start_web_streaming(self):
        self.web_server.start()

    def _generate_frame(self):
        while True:
            with self.lock:
                if self.frame is None:
                    continue
                (flag, encodedImage) = cv2.imencode(".jpg", self.frame)
                if not flag:
                    continue
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       bytearray(encodedImage) + b'\r\n')

    def end(self):
        print("Done AbstractWebServerPipelinePattern!")

        print("[1/1] Turn off web_server")
        self.web_server.end()

        print("\n")


import time
class PipelinePattern(AbstractWebServerPipelinePattern):
    def __init__(self, drone, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drone = drone
        self.command = None

        self.state = True
        self.last_t = time.time()

    def execute(self):
        try:
            while self.state:
                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 2. Get the data from the image and compute the command as output
                self.command, value = self.command_recognition.execute(frame)

                # 3. Execute the command
                elapsed_t = time.time() - self.last_t
                if elapsed_t > 0.5:
                    self.control_module.execute(self.command, value)
                    if self.command != Command.NONE:
                        self.last_t = time.time()

                # 4. Edit frame
                frame = self.command_recognition.edit_frame(frame)
                frame = self.drone_edit_frame.edit(frame)

                # global lock, outputFrame
                with self.lock:
                    self.frame = frame.copy()

                # 5. Display frame
                self.state = self.displayer.show(frame)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
            raise e
        finally:
            self.end()

    def end(self):
        print("Done PipelinePattern!")
        self.state = False

        print("[1/7] Turn off super()\n")
        super().end()

        print("[2/7] Turn off stream_module")
        self.stream_module.end()
        print("[3/7] Turn off command_recognition")
        self.command_recognition.end()
        print("[4/7] Turn off control_module")
        self.control_module.end()
        print("[5/7] Turn off drone_edit_frame")
        self.drone_edit_frame.end()
        print("[6/7] Turn off displayer")
        self.displayer.end()
        print("[7/7] Turn off drone")
        self.drone.end()

        print("\n")


class ReasoningPipelinePattern(AbstractWebServerPipelinePattern):
    def __init__(self, drone, reasoning_agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drone = drone
        self.reasoning_agent = reasoning_agent
        self.command = None

        self.state = True

    def execute(self):
        try:
            while self.state:
                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 3. Get the data from the image and compute the command as output
                self.command, value = self.command_recognition.execute(frame)

                self.command, value = self.reasoning_agent.execute(self.command, value)

                # 4. Execute the command
                self.control_module.execute(self.command, value)

                # 5. Edit frame
                frame = self.command_recognition.edit_frame(frame)
                frame = self.drone_edit_frame.edit(frame)

                # global lock, outputFrame
                with self.lock:
                    self.frame = frame.copy()

                # 6. Display frame
                self.state = self.displayer.show(frame)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
            raise e
        finally:
            self.end()

    def end(self):
        print("Done ReasoningPipelinePattern!")
        self.state = False

        print("[1/7] Turn off super()\n")
        super().end()

        print("[2/7] Turn off stream_module")
        self.stream_module.end()
        print("[3/7] Turn off command_recognition")
        self.command_recognition.end()
        print("[4/7] Turn off control_module")
        self.control_module.end()
        print("[5/7] Turn off drone_edit_frame")
        self.drone_edit_frame.end()
        print("[6/7] Turn off displayer")
        self.displayer.end()
        print("[7/7] Turn off drone")
        self.drone.end()

        print("\n")


