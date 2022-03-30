from modules import drone, VideoStreamModule

import cv2


tello = drone.DJITello()

video_stream_module = VideoStreamModule.VideoDroneStream(tello)

try:
    while True:
        cv2.imshow("Video", video_stream_module.get_stream_frame())
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
    video_stream_module.release_stream()


tello.end()