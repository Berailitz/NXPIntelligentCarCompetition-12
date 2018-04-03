"""define all apis under /api/"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from flask import request, Response
from flask_restful import Resource, Api, reqparse
from .mess import fun_logger
from .camera import generate_picture, Camera
from .restful_helper import parse_one_arg


my_camera = Camera()


def create_api():
    """return api object at startup"""
    api = Api()
    api.add_resource(StatuspAPI, '/api/status')
    return api


def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_picture(my_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


class StatuspAPI(Resource):
    """handle /api/status"""
    @staticmethod
    def get():
        return {'status': 0, 'data': {'速度': '2333m/s', '长宽比': '0.23', '是否发生事故': '否'}}
