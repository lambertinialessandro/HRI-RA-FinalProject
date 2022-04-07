import cv2
import schedule


class Window:
    def __init__(self, get_battery, get_fps, on_closed, name="Video"):
        self.get_battery = get_battery
        self.get_fps = get_fps
        self.on_closed = on_closed
        self.name = name

        # cv2.namedWindow(self.name)

        self.battery = None
        self.__update_battery()
        schedule.every(10).seconds.do(self.__update_battery)

    def __update_battery(self):
        self.battery = self.get_battery()

    def _write(self, frame, text, position=(0, 0), font_scale=1, color=(0, 0, 0), thickness=1):
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_PLAIN, fontScale=font_scale, color=color, thickness=thickness)

    def show(self, frame):
        self._write(frame, f"Battery: {self.battery}%", position=(10, 15), color=(0, 0, 255))
        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            self.on_closed()

    def destroy(self):
        cv2.destroyAllWindows()
