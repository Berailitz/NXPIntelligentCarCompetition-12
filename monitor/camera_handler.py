from collections import defaultdict
import base64
import logging
import cv2
from .ocr import OCRHandle


class CameraUnit(object):
    def __init__(self, video_id):
        self.video_id = video_id
        self.camera = cv2.VideoCapture(video_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.ocr_handle = OCRHandle()
        self.frame_index = 0

    def detect_video(self):
        self.frame_index += 1
        result = {'picture': '', 'status': {
            'frame_index': self.frame_index, 'num': -1}}
        try:
            res, frame = self.camera.read()
            if res:
                self.ocr_handle.analyse_img(frame)
                result['status'] = self.ocr_handle.status
                result['video'] = {}
                try:
                    for label, video in self.ocr_handle.videos.items():
                        retval, buffer = cv2.imencode('.jpg', video)
                        result['video'][label] = base64.b64encode(buffer).decode('utf-8')
                except:
                    pass
        except Exception as e:
            logging.exception(e)
        return result

    def __del__(self):
        logging.warning(f"Closing camera `{self.video_id}`.")
        self.camera.release()


class CameraHandler(defaultdict):
    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = CameraUnit(video_id)
        return self[video_id]
