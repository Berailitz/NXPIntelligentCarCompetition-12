from collections import defaultdict
import base64
import cv2
import logging
from .ocr import OCRHandle


class CameraUnit(object):
    def __init__(self, video_id):
       self.camera = cv2.VideoCapture(video_id)
       self.ocr_handle = OCRHandle()
       self.frame_index = 0

    def detect_video(self):
        self.frame_index += 1
        res, frame = self.camera.read()
        try:
            ocr_result = self.ocr_handle.analyse_img(frame)
            retval, buffer = cv2.imencode('.jpg', self.ocr_handle.orig)
        except Exception as e:
            logging.exception(e)
            ocr_result = "-1"
            ocr_result = self.ocr_handle.analyse_img(frame)
        return {'picture': base64.b64encode(
            buffer).decode('utf-8'), 'status': {'frame_index': self.frame_index, 'num': ocr_result}}



class CameraHandler(defaultdict):

    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = CameraUnit(video_id)
        return self[video_id]
