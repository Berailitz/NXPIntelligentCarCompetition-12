"""main module including create_app()"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-


import logging
import os
from multiprocessing import Process
from tornado import httpserver, ioloop, web
from .config import SERVER_PORT, SERVER_ADDRESS
from .handler import IndexHandler, SocketHandler
from .mess import get_current_time, set_logger


class WebProcess(Process):
    def __init__(self):
        super().__init__()

    def run(self):
        """create initialized flask app, compatible with uwsgi"""
        app = web.Application(
            [
                (r'/live/(?P<video_id>.+)', IndexHandler),
                (r'/api/live/(?P<video_id>.+)', SocketHandler),
            ],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"))
        http_server = httpserver.HTTPServer(app)
        http_server.listen(port=SERVER_PORT, address=SERVER_ADDRESS)
        logging.info("Starting web server...")
        ioloop.IOLoop.instance().start()
