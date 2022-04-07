import cv2
import schedule


class Window:
    instance = None

    def __init__(self, get_battery, get_fps, on_closed, name="Video"):
        Window.instance = self

        self.get_battery = get_battery
        self.get_fps = get_fps
        self.on_closed = on_closed
        self.name = name

        self.frame = None

        cv2.namedWindow(self.name)

        self.battery = None
        self._update_battery()
        schedule.every(10).seconds.do(self._update_battery)

    def _update_battery(self):
        self.battery = self.get_battery()

    def write(self, text, position=(0, 0), font_scale=1, color=(0, 0, 0), thickness=1):
        cv2.putText(self.frame, text, position, cv2.FONT_HERSHEY_PLAIN, font_scale, color, thickness)

    def draw_circle(self, center, radius, color=(0, 0, 0), thickness=1):
        cv2.circle(self.frame, center, radius, color, thickness, cv2.FILLED)

    def draw_rectangle(self, x, y, w, h, color=(0, 0, 0), thickness=1):
        cv2.rectangle(self.frame, (x, y), (w, h), color, thickness)

    def show(self, frame):
        self.frame = frame
        self.write(f"Battery: {self.battery}%", position=(10, 15), color=(0, 0, 255))
        self.write(f"FPS: {self.battery}%", position=(10, 30), color=(0, 0, 255))

        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            self.on_closed()
            self.destroy()

    def destroy(self):
        Window.instance = None
        cv2.destroyAllWindows()
