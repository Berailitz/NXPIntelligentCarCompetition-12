from .sensor.result import result as Result


class CameraHandler(object):
    """An Event-like class that signals all active clients when a new frame is
    available."""
    def __init__(self):
        self.my_result = Result()
        self.result_dict = self.my_result.detect_video()

    def update(self):
        self.result_dict = self.my_result.detect_video()
        while not self.result_dict:
            self.result_dict = self.my_result.detect_video()
        return self.result_dict
