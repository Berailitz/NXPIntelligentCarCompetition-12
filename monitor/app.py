"""main module including create_app()"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-


import os
from tornado import httpserver, web
from .config import SSL_CERT_FILE, SSL_KEY_FILE, SERVER_PORT, SERVER_ADDRESS
from .handler import IndexHandler, SocketHandler
from .mess import set_logger


def create_app(log_path='log'):
    """create initialized flask app, compatible with uwsgi"""
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    set_logger(f'{log_path}/log_{os.getpid()}.txt')
    app = web.Application(
        [
            (r'/live/(?P<video_id>\d+)', IndexHandler),
            (r'/api/live/(?P<video_id>\d+)', SocketHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"))
    http_server = httpserver.HTTPServer(app, ssl_options={
        "certfile": SSL_CERT_FILE,
        "keyfile": SSL_KEY_FILE,
    })
    http_server.listen(port=SERVER_PORT, address=SERVER_ADDRESS)
    return app
