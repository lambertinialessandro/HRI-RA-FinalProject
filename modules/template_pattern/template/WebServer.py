import flask
import threading


class WebServer:

    def __init__(self, generate_frame, ip: str = "0.0.0.0", port: int = 8080):
        self.ip = ip
        self.port = port
        self._generate_frame = generate_frame
        self._thread = None

        self._init_flask()

    def _init_flask(self):
        self._app = flask.Flask(__name__)

        @self._app.route("/")
        def index():
            return flask.render_template("modules/templates/index.html")

        @self._app.route("/video_feed")
        def video_feed():
            return flask.Response(self._generate_frame(),
                                  mimetype="multipart/x-mixed-replace; boundary=frame")

    def _start_flask(self):
        self._app.run(host=self.ip, port=self.port, debug=True, threaded=True, use_reloader=False)

    def start(self):
        self._thread = threading.Thread(target=self._start_flask)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        if self._thread is not None:
            pass  #TODO: stop thread
