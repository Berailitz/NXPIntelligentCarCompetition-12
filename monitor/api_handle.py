"""define all apis under /api/"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from flask import request, make_response
from flask_restful import Resource, Api, reqparse
from .mess import fun_logger
from .camera_handler import CameraHandler
from .restful_helper import parse_one_arg


camera_handler = CameraHandler()


def create_api():
    """return api object at startup"""
    api = Api()
    api.add_resource(StatuspAPI, '/api/status')
    return api


class StatuspAPI(Resource):
    """handle /api/status"""
    @staticmethod
    def get():
        return {'status': 0, 'data': camera_handler.update_status()}
