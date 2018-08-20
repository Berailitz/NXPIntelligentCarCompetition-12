from .image_processer import ImageProcesser


class Crossfinder(ImageProcesser):
    def __init__(self, queues):
        super().__init__(queues, 'image_queue_b')

    def analyse(self, raw_img):
        pass
