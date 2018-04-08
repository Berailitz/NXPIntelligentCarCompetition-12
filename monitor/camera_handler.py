import logging
import numpy
from .sensor.result import result as Result


class CameraHandler(object):
    """An Event-like class that signals all active clients when a new frame is
    available."""
    def __init__(self):
        self.my_result = Result()
        self.result_dict = self.my_result.detect_video()

    def update_image(self):
        while not self.result_dict:
            self.result_dict = self.my_result.detect_video()
        logging.info(f"Ave: {numpy.mean(self.result_dict['picture'])}")
        return self.result_dict['picture']

    def update_status(self):
        while not self.result_dict:
            self.result_dict = self.my_result.detect_video()
        return {'picture': '/video_feed', 'status': self.result_dict['data']}
