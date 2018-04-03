"""define all apis under /api/"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from flask import request, Response
from flask_restful import Resource, Api, reqparse
from .mess import fun_logger
from .restful_helper import parse_one_arg


def create_api():
    """return api object at startup"""
    api = Api()
    api.add_resource(StatuspAPI, '/api/status')
    return api


class StatuspAPI(Resource):
    """handle /api/status"""
    @staticmethod
    def get():
        return {'status': 0, 'data': {'速度': '2333m/s', '长宽比': '0.23', '是否发生事故': '否'}}
