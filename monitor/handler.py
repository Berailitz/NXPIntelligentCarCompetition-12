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

    def open(self, video_id):
        logging.info(f'Open camera `{video_id}`.')
        self.camera = active_cameras[int(video_id)]

    def on_message(self, message):
        """ Retrieve image ID from database until different from last ID,
        then retrieve image, de-serialize, encode and send to client. """
        try:
            index = int(message) + 1
        except ValueError:
            index = 1
        if index % 100 == 0:
            logging.info(f'Sending frame `{index}`.')
        update_dict = self.camera.detect_video()
        update_dict['picture'] = base64.b64encode(
            update_dict['picture']).decode('utf-8')
        update_dict['index'] = index
        self.write_message(json.dumps(update_dict, ensure_ascii=False))
