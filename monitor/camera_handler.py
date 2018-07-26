from collections import defaultdict
import base64
import cv2
from .ocr import analyse_img


class CameraUnit(object):
    def __init__(self, video_id):
       self.camera = cv2.VideoCapture(video_id)
       self.frame_index = 0

    def detect_video(self):
        self.frame_index += 1
        res, frame = self.camera.read()
        retval, buffer = cv2.imencode('.jpg', frame)
        return {'picture': base64.b64encode(
            buffer).decode('utf-8'), 'status': {'frame_index': self.frame_index, 'num': analyse_img(frame)}}



class CameraHandler(defaultdict):

    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = CameraUnit(video_id)
        return self[video_id]
