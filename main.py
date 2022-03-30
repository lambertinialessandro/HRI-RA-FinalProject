
from modules.factories.GlobalFactory import GlobalFactory

import cv2

fim = GlobalFactory()
video_stream_module, command_recognition, control = fim.createInput(GlobalFactory.VideoPC)

try:
    while True:

        cv2.imshow("Webcam", video_stream_module.get_stream())
        key = cv2.waitKey(1)
        if key == 27: # ESC
            break
except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
    video_stream_module.release_stream()
