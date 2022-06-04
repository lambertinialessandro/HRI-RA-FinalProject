
from abc import ABC, abstractmethod
# import time
import threading
import cv2

# # TODO
# # link between 2 files from different hierarchy maybe to be fixed
# from modules.control.ControlModule import Command
from modules.window.Window import Window
from modules.template_pattern.WebServer import WebServer


class AbstractTemplatePattern(ABC):
    def __init__(self, stream_module, command_recognition,
                 control_module, drone_edit_frame):
        self.stream_module = stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module
        self.drone_edit_frame = drone_edit_frame
        self.displayer = Window(binded_obj=self)

        # TODO
        # fix command block
        self.mutex = threading.Lock()

    @classmethod
    @abstractmethod
    def execute(cls):
        pass

    @classmethod
    @abstractmethod
    def end(cls):
        pass


class AbstractWebServerTemplatePattern(AbstractTemplatePattern):
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
        print("Done AbstractWebServerTemplatePattern!")

        print("[1/1] Turn off web_server")
        self.web_server.end()

        print("\n")


class TemplatePattern(AbstractWebServerTemplatePattern):
    def __init__(self, drone, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drone = drone
        self.command = None

        self.state = True

    def execute(self):
        try:
            while self.state:
                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 2. Get the data from the image and compute the command as output
                self.command, value = self.command_recognition.execute(frame)

                # 3. Execute the command
                self.control_module.execute(self.command, value)

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
        print("Done TemplatePattern!")
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


class ReasoningTemplatePattern(AbstractWebServerTemplatePattern):
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
        print("Done ReasoningTemplatePattern!")
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


















#
#
# from modules.window.Window import Window
#
#
# class VideoTemplatePattern(AbstractTemplatePattern):
#     def __init__(self, video_stream_module, command_recognition, control_module, drone):
#         super().__init__(video_stream_module, command_recognition, control_module)
#
#         self.drone = drone
#
#         self.command = None
#
#         self.window = None
#
#         self.pTime = 0
#         self.cTime = 0
#
#     def execute(self):
#         self.window = Window(self.drone, on_closed=self.end)
#
#         try:
#             while True:
#                 schedule.run_pending()  # update the battery if 10 seconds have passed
#
#                 # 1. Get the frame
#                 frame = self.stream_module.get_stream_frame()
#
#                 # 2. Get the command
#                 self.command, value = self.command_recognition.get_command(frame)
#
#                 # 3. Execute the comand
#                 if not self.mutex.locked() and self.command != Command.NONE:
#                     if self.command == Command.LAND:
#                         self.mutex.acquire()
#
#                     print(f"Command: {self.command} Value: {value}")
#
#                     self.control_module.execute(self.command, value)
#                     self.command = None
#
#                 self.cTime = time.time()
#                 fps = int(1 / (self.cTime - self.pTime))
#                 self.pTime = self.cTime
#
#                 self.window.show(frame)
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.end()
#
#     def end(self):
#         print("Done!")
#
#         self.stream_module.end()
#         self.command_recognition.end()
#         self.control_module.end()
#
#         schedule.clear()
#
#
# class AudioTemplatePattern(AbstractTemplatePattern):
#     def __init__(self, audio_stream_module, command_recognition, control_module, drone):
#         super().__init__(audio_stream_module, command_recognition, control_module)
#         self.drone = drone
#         self.battery = drone.battery
#         schedule.every(10).seconds.do(self.__update_battery)
#
#     def __update_battery(self):
#         self.battery = self.drone.battery
#         print(f"Battery: {self.battery}%")
#
#     def execute(self):
#         try:
#             while True:
#                 schedule.run_pending()  # update the battery if 10 seconds have passed
#
#                 word = self.stream_module.get_stream_word()
#                 command, value = self.command_recognition.get_command(word)
#                 self.control_module.execute(command, value)
#
#                 if command == Command.STOP_EXECUTION:
#                     break
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.end()
#
#     def end(self):
#         print("Done!")
#
#         self.stream_module.end()
#         self.command_recognition.end()
#         self.control_module.end()
#
#         schedule.clear()
