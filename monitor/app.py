"""main module including create_app()"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-


import os
from tornado import httpserver, web
from .config import SERVER_PORT, SERVER_ADDRESS
from .handler import IndexHandler, SocketHandler
from .mess import get_current_time, set_logger


def create_app(log_path='log'):
    """create initialized flask app, compatible with uwsgi"""
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    set_logger('{}/log_{}_{}.txt'.format(log_path, get_current_time(), os.getpid()))
    app = web.Application(
        [
            (r'/live/(?P<video_id>.+)', IndexHandler),
            (r'/api/live/(?P<video_id>.+)', SocketHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"))
    http_server = httpserver.HTTPServer(app)
    http_server.listen(port=SERVER_PORT, address=SERVER_ADDRESS)
    return app
