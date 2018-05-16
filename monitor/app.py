"""main module including create_app()"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import base64
import json
import os
from tornado import websocket, web
from .camera_handler import CameraHandler
from .mess import set_logger


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class SocketHandler(websocket.WebSocketHandler):
    """ Handler for websocket queries. """

    def __init__(self, *args, **kwargs):
        """ Initialize the Redis store and framerate monitor. """
        super(SocketHandler, self).__init__(*args, **kwargs)
        self._store = CameraHandler()

    def on_message(self, message):
        """ Retrieve image ID from database until different from last ID,
        then retrieve image, de-serialize, encode and send to client. """
        image_dict = self._store.update()
        image_dict['picture'] = base64.b64encode(image_dict['picture']).decode('utf-8')
        self.write_message(json.dumps(image_dict, ensure_ascii=False))


def create_app(log_path='log'):
    """create initialized flask app, compatible with uwsgi"""
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    set_logger(f'{log_path}/log_{os.getpid()}.txt')
    app = web.Application(
        [
            (r'/', IndexHandler),
            (r'/ws/video', SocketHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"))
    return app
