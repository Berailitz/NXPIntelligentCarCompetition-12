import logging
import os
import time
from multiprocessing import Process
from .config import STANDARD_BASE_INTERVAL


class ImageProcesser(Process):
    def __init__(self, queues, image_queue_name):
        super().__init__()
        self.queues = queues
        self.image_queue_name = image_queue_name
        self.last_frame_timestamp = None

    def write_serial(self, reult_in_bytes) -> None:
        self.queues['bytes_queue'].put(reult_in_bytes)

    def analyse(self, raw_img) -> None:
        raise NotImplementedError

    def run(self):
        print("Start `{}` process at PID `{}`.".format(self.__class__.__name__, os.getpid()))
        while True:
            time.sleep(STANDARD_BASE_INTERVAL * 2)
            image = self.queues[self.image_queue_name].get()
            if image is not None:
                self.analyse(image)
                if self.last_frame_timestamp is None:
                    self.last_frame_timestamp = time.time()
                else:
                    now_timestamp = time.time()
                    logging.info("FPS of `{}`: `{}`.".format(self.__class__.__name__, 1 / (now_timestamp - self.last_frame_timestamp)))
                    self.last_frame_timestamp = now_timestamp
