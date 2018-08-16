import base64
import json
import logging
from tornado import websocket, web
from .camera_handler import CameraHandler

active_cameras = CameraHandler()


class IndexHandler(web.RequestHandler):
    def get(self, video_id):
        self.render('live.html', video_id=video_id)


class SocketHandler(websocket.WebSocketHandler):
    """ Handler for websocket queries. """
    def __init__(self, application, request):
        """ Initialize the Redis store and framerate monitor. """
        super().__init__(application, request)
        self.camera = None
        self.video_id = None

    def check_origin(self, origin):
        return True

    def open(self, video_id):
        logging.info('Open camera `{}`.'.format(video_id))
        self.video_id = video_id
        self.camera = active_cameras[video_id]

    def on_message(self, message):
        """ Retrieve image ID from database until different from last ID,
        then retrieve image, de-serialize, encode and send to client. """
        try:
            index = int(message) + 1
        except ValueError:
            index = 1
        if index % 100 == 0:
            logging.info('Sending frame `{}`.'.format(index))
        update_dict = self.camera.detect_video()
        self.write_message(json.dumps(update_dict, ensure_ascii=False))

    def on_close(self):
        logging.warning("WebSocket `{}` closed.".format(self.video_id))
        self.camera.close()
