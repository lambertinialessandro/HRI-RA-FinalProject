
from abc import ABC, abstractmethod
import time
import schedule
import flask
import threading
import cv2

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command
from modules.window.Window import Window


class AbstractTemplatePattern(ABC):
    def __init__(self, stream_module, command_recognition, control_module,
                 drone_edit_frame):
        self.stream_module = stream_module
        self.command_recognition = command_recognition
        self.control_module = control_module
        self.drone_edit_frame = drone_edit_frame
        self.displayer = Window(cls=self)

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


# import flask
# import threading
# import cv2
# lock = threading.Lock()
# outputFrame = None
# app = flask.Flask(__name__)

class TemplatePattern(AbstractTemplatePattern):
    def __init__(self, drone, *args):
        super().__init__(*args)
        self.drone = drone
        self.command = None

        self.frame = None

        self.ip = None
        self.port = None
        self.lock = threading.Lock()
        self.webThread = None

    def execute(self):
        self.state = True

        try:
            while self.state:

                # 1. Get the frame
                frame = self.stream_module.get_stream_frame()

                # 3. Get the data from the image and compute the command as output
                self.command, value = self.command_recognition.execute(frame)

                # 4. Execute the comand
                self.control_module.execute(self.command, value)

                # 5. Edit frame
                frame = self.command_recognition.edit_frame(frame)
                frame = self.drone_edit_frame.edit(frame)
                #self.frame = frame

                #global lock, outputFrame
                with self.lock:
                    self.frame = frame.copy()

                # 6. Display frame
                self.state = self.displayer.show(frame)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
            #self.execute()
        finally:
            self.end()

    def start_web_streaming(self, ip:str = "0.0.0.0", port:int = 8080):
        self.ip = ip
        self.port = port
        app = flask.Flask(__name__)

        @app.route("/")
        def index():
        	return flask.render_template("index.html")
        @app.route("/video_feed")
        def video_feed():
        	return flask.Response(generate(),
        		mimetype = "multipart/x-mixed-replace; boundary=frame")

        def generate():
            #global outputFrame, lock
            while True:
                with self.lock:
                    if self.frame is None:
                        continue
                    (flag, encodedImage) = cv2.imencode(".jpg", self.frame)
                    if not flag:
                        continue
                    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                          bytearray(encodedImage) + b'\r\n')

        def startWebServer():
            app.run(host=self.ip, port=self.port, debug=True,
                    threaded=True, use_reloader=False)

        self.webThread = threading.Thread(target=startWebServer)
        self.webThread.daemon = True
        self.webThread.start()

    def end(self):
        print("Done!")
        self.state = False

        # print("[1/9] Turn off Window")
        # self.window.end()

        print("[1/6] Turn off stream_module")
        self.stream_module.end()
        # print("[3/9] Turn off frame_tracker")
        # self.frame_tracker.end()
        print("[2/6] Turn off command_recognition")
        self.command_recognition.end()
        print("[3/6] Turn off control_module")
        self.control_module.end()
        # print("[6/9] Turn off tracking_edit_frame")
        # self.tracking_edit_frame.end()
        print("[4/6] Turn off drone_edit_frame")
        self.drone_edit_frame.end()
        print("[5/6] Turn off displayer")
        self.displayer.end()

        #print("[9/9] Turn off schedule")
        #schedule.clear()

        print("[6/6] Turn off drone")
        self.drone.end()

        if self.webThread is not None:
            self.webThread


from modules.window.Window import Window

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


