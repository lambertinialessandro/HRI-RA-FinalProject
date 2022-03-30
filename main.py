from modules import drone, VideoStreamModule, ControlModule

import cv2


tello = drone.DJITello()

# 1: VideoStreamModule
# video_stream_module = VideoStreamModule.VideoDroneStream(tello)
video_stream_module = VideoStreamModule.WebcamStream()
# 2: CommandRecognitionModule
# TODO
# 3: ControlModule
control_module = ControlModule.ControlModule(tello)

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