
from abc import ABC, abstractmethod
import time
import schedule
from threading import Lock

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command
from modules.window.Window import Window


class AbstractTemplatePattern(ABC):
    def __init__(self, stream_module, frame_tracker, command_recognition, control_module,
                 tracking_edit_frame, drone_edit_frame, displayer):
        self.stream_module = stream_module
        self.frame_tracker = frame_tracker
        self.command_recognition = command_recognition
        self.control_module = control_module
        self.tracking_edit_frame = tracking_edit_frame
        self.drone_edit_frame = drone_edit_frame
        self.displayer = displayer

        # TODO
        # fix command block
        self.mutex = Lock()

    @classmethod
    @abstractmethod
    def execute(cls):
        pass

    @classmethod
    @abstractmethod
    def end(cls):
        pass


class TemplatePattern(AbstractTemplatePattern):
    def __init__(self, *args):
        super().__init__(*args)

        self.command = None

    def execute(self):
        state = True

        try:
            while state:

                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 2. Get the data from the image
                tracking_data = self.frame_tracker.analyze_frame(frame)

                # 3. Get the command
                self.command, value = self.command_recognition.execute(tracking_data)

                # 4. Execute the comand
                self.control_module.execute(self.command, value)
                self.command = None

                # 5. Edit frame
                frame = self.tracking_edit_frame.edit(frame, tracking_data)
                frame = self.drone_edit_frame.edit(frame)

                # 6. Display frame
                state = self.displayer.show(frame)
        # except KeyboardInterrupt:
        #     pass
        finally:
            self.end()

    def end(self):
        print("Done!")

        self.stream_module.end()
        self.frame_tracker.end()
        self.command_recognition.end()
        self.control_module.end()
        self.tracking_edit_frame.end()
        self.drone_edit_frame.end()
        self.displayer.end()

        schedule.clear()

class VideoTemplatePattern(AbstractTemplatePattern):
    def __init__(self, video_stream_module, command_recognition, control_module, drone):
        super().__init__(video_stream_module, command_recognition, control_module)

        self.drone = drone

        self.command = None

        self.window = None

        self.pTime = 0
        self.cTime = 0

    def execute(self):
        self.window = Window(self.drone, on_closed=self.end)

        try:
            while True:
                schedule.run_pending()  # update the battery if 10 seconds have passed

                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 2. Get the command
                self.command, value = self.command_recognition.get_command(frame)

                # 3. Execute the comand
                if not self.mutex.locked() and self.command != Command.NONE:
                    if self.command == Command.LAND:
                        self.mutex.acquire()

                    print(f"Command: {self.command} Value: {value}")

                    self.control_module.execute(self.command, value)
                    self.command = None

                self.cTime = time.time()
                fps = int(1/(self.cTime - self.pTime))
                self.pTime = self.cTime

                self.window.show(frame)
        except KeyboardInterrupt:
            pass
        finally:
            self.end()

    def end(self):
        print("Done!")

        self.stream_module.end()
        self.command_recognition.end()
        self.control_module.end()

        schedule.clear()


class AudioTemplatePattern(AbstractTemplatePattern):
    def __init__(self, audio_stream_module, command_recognition, control_module, drone):
        super().__init__(audio_stream_module, command_recognition, control_module)
        self.drone = drone
        self.battery = drone.battery
        schedule.every(10).seconds.do(self.__update_battery)

    def __update_battery(self):
        self.battery = self.drone.battery
        print(f"Battery: {self.battery}%")

    def execute(self):
        try:
            while True:
                schedule.run_pending()  # update the battery if 10 seconds have passed

                word = self.stream_module.get_stream_word()
                command, value = self.command_recognition.get_command(word)
                self.control_module.execute(command, value)

                if command == Command.STOP_EXECUTION:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.end()

    def end(self):
        print("Done!")

        self.stream_module.end()
        self.command_recognition.end()
        self.control_module.end()

        schedule.clear()


