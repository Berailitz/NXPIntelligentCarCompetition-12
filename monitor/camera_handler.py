from collections import defaultdict
import base64
import logging
import cv2
import serial
from .config import IS_SERIAL_ENABLED, IS_WEB_VIDEO_ENABLED
from .credentials import SERIAL_BAUDRATE, SERIAL_PORT
from .ocr import OCRHandle


class CameraUnit(object):
    def __init__(self, video_id):
        try:
            self.video_id = int(video_id)
        except ValueError:
            self.video_id = video_id
        self.camera = None
        self.open_camera()
        self.ocr_handle = OCRHandle()
        self.frame_index = 0
        self.is_opened = False
        if IS_SERIAL_ENABLED:
            logging.warning("Open serial port `{}` at baudrate `{}`.".format(SERIAL_PORT, SERIAL_BAUDRATE))
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.video_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.is_opened = self.camera and self.camera.isOpened()
        if not self.is_opened:
            raise SystemError("Cannot open camera `{}`.".format(self.video_id))

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
                    if IS_WEB_VIDEO_ENABLED:
                        for label, video in self.ocr_handle.videos.items():
                            retval, buffer = cv2.imencode('.jpg', video)
                            result['video'][label] = base64.b64encode(buffer).decode('utf-8')
                except:
                    pass
            else:
                logging.warning("No frame read.")
                self.open_camera()
        except Exception as e:
            logging.exception(e)
        return result

    def __del__(self):
        if self.is_opened:
            self.close()

    def close(self):
        logging.warning("Closing camera `{}`.".format(self.video_id))
        self.camera.release()
        if IS_SERIAL_ENABLED:
            logging.warning("Closing serial port `{}`.".format(SERIAL_PORT))
            self.ser.close()


class CameraHandler(defaultdict):
    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = CameraUnit(video_id)
        return self[video_id]
