import time
from multiprocessing import Process
from .config import SCAN_INTERVAL


class ImageProcesser(Process):
    def __init__(self, queues, image_queue_name):
        super().__init__()
        self.queues = queues
        self.image_queue_name = image_queue_name

    def write_serial(self, reult_in_bytes) -> None:
        self.queues['bytes_queue'].put(reult_in_bytes)

    def analyse(self, raw_img) -> None:
        raise NotImplementedError

    def run(self):
        while True:
            time.sleep(SCAN_INTERVAL)
            image = self.queues[self.image_queue_name].get()
            if image is not None:
                self.analyse(image)
            else:
                return
