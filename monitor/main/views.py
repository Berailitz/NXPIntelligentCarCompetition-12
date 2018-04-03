"""main views and blueprint"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, make_response, render_template
from ..mess import fun_logger

def create_main_blueprint():
    """create and return main blueprint, which should be registered later"""
    main_blueprint = Blueprint('main', __name__, template_folder='templates')
    main_blueprint.add_url_rule('/', 'index', show_index_page)
    return main_blueprint

def show_index_page():
    return make_response(render_template('index.html', page_title='IP地址查询', assert_url='index'))
