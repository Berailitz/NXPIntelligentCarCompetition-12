import base64
import logging
import os
import time
import cv2
from collections import defaultdict
from multiprocessing import Process
from .config import IS_SERIAL_ENABLED, IS_WEB_VIDEO_ENABLED, OCR_DO_USE_NCS, CAMERA_HEIGHT, CAMERA_WIDTH, STANDARD_BASE_INTERVAL, CHESS_CAMERA_ID, MAIN_CAMERA_ID
from .credentials import SERIAL_BAUDRATE, SERIAL_PORT
from .ocr import OCRHandle


class CameraUnit(object):
    def __init__(self, video_id):
        try:
            self.video_id = int(video_id)
        except ValueError:
            self.video_id = video_id
        self.camera = None
        self.ocr_handle = None
        self.frame_index = 0

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.video_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 10)
        for i in range(20):
            self.camera.read()

    def open(self):
        self.open_camera()
        if not self.camera.isOpened():
            raise SystemError("Cannot open camera `{}`.".format(self.video_id))

    def get_frame(self):
        self.frame_index += 1
        try:
            res, frame = self.camera.read()
            if res:
                return frame
            else:
                logging.warning("No frame read.")
                self.close_camera()
                self.open_camera()
                return self.get_frame()
        except Exception as e:
            logging.exception(e)
        # return result

    def __del__(self):
        if self.camera is not None:
            self.camera.release()
        if self.ocr_handle is not None:
            self.ocr_handle.close()

    def close_camera(self):
        logging.warning("Closing camera `{}`.".format(self.video_id))
        self.camera.release()
        self.camera = None

    def close(self):
        self.close_camera()
        if OCR_DO_USE_NCS:
            logging.warning("Closing NCS device.")
            self.ocr_handle.close()
            self.ocr_handle = None


class CameraProcess(Process):
    def __init__(self, queues):
        super().__init__()
        self.camera = None
        self.chess_camera = None
        self.queues = queues
        self.real_frame_index = 0

    def open_camera(self):
        self.camera = CameraUnit(MAIN_CAMERA_ID)
        self.camera.open()
        self.chess_camera = CameraUnit(CHESS_CAMERA_ID)
        self.chess_camera.open()
        self.real_frame_index = 0

    def close_camera(self):
        if self.camera is not None:
            self.camera.close()
            self.camera = None
        if self.chess_camera is not None:
            self.chess_camera.close()
            self.chess_camera = None

    def run(self):
        logging.warning("Start `{}` process at PID `{}`.".format(self.__class__.__name__, os.getpid()))
        self.open_camera()
        while True:
            task = self.queues['task_queue'].get()
            if task is None:
                self.close_camera()
                return
            else:
                frame = self.camera.get_frame()
                if self.queues['image_queue_a'].qsize() <= 1:
                    self.queues['image_queue_a'].put(frame.copy())
                if self.queues['image_queue_b'].qsize() <= 1:
                    self.queues['image_queue_b'].put(frame)
                chess_frame = self.chess_camera.get_frame()
                if self.queues['image_queue_c'].qsize() <= 1:
                    self.queues['image_queue_c'].put(chess_frame)
        logging.warning("End `{}` process at PID `{}`.".format(self.__class__.__name__, os.getpid()))
