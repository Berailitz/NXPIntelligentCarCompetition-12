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
            if frame is not None:
                self.ocr_handle.analyse_img(frame)
                result['video'] = {}
                retval, buffer_orig = cv2.imencode('.jpg', self.ocr_handle.orig)
                result['video']['video_raw'] = base64.b64encode(buffer_orig).decode('utf-8')
                if self.ocr_handle.cut is not None:
                    retval, buffer_cut = cv2.imencode('.jpg', self.ocr_handle.cut)
                    result['video']['video_cut'] = base64.b64encode(buffer_cut).decode('utf-8')
                else:
                    result['video']['video_cut'] = ''
                result['status'] = self.ocr_handle.status
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
