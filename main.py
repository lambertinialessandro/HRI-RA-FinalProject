from modules import VideoStreamModule


import cv2


video_stream_module = VideoStreamModule.WebcamStream()

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
