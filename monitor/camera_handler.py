from collections import defaultdict
import base64
import logging
import cv2
import serial
from .config import IS_SERIAL_ENABLED, IS_WEB_ENABLED
from .credentials import SERIAL_BAUDRATE, SERIAL_PORT
from .ocr import OCRHandle


class CameraUnit(object):
    def __init__(self, video_id):
        try:
            self.video_id = int(video_id)
        except ValueError:
            self.video_id = video_id
        self.camera = cv2.VideoCapture(self.video_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.ocr_handle = OCRHandle()
        self.frame_index = 0
        if IS_SERIAL_ENABLED:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)

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
                    if IS_SERIAL_ENABLED:
                        self.ser.write(self.ocr_handle.serial_data)
                    if IS_WEB_ENABLED:
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
        if IS_SERIAL_ENABLED:
            self.ser.close()


class CameraHandler(defaultdict):
    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = CameraUnit(video_id)
        return self[video_id]
