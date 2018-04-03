"""main module including create_app()"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
import os
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from .api_handle import create_api, video_feed
from .main.views import create_main_blueprint
from .mess import set_logger


def create_app(log_path='log'):
    """create initialized flask app, compatible with uwsgi"""
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    set_logger(f'{log_path}/log_{os.getpid()}.txt')
    app = Flask(__name__, static_folder="main/static")
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    api = create_api()
    api.init_app(app)
    main_blueprint = create_main_blueprint()
    app.register_blueprint(main_blueprint)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.add_url_rule('/video_feed', 'video_feed', video_feed)
    logging.info('%r', app.view_functions)
    logging.info('%r', app.url_map)
    return app
