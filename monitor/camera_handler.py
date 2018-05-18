from collections import defaultdict
from .sensor.result import result as Result


class CameraHandler(defaultdict):

    def __init__(self):
        super().__init__()

    def __missing__(self, video_id):
        self[video_id] = Result(video_id)
        return self[video_id]
