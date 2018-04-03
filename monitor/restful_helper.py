"""handle restful related problems"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

def get_arg(current, default=None, call_back=lambda arg: arg):
    """check whether a value is None (or equal to False), return default value, None by default, or call_back(value)"""
    if current:
        return call_back(current)
    return default

def parse_one_arg(parser, arg_key, type, default=None, call_back=lambda arg: arg):
    """prase all args, `None` by default, return args dict"""
    parser.add_argument(arg_key, type=type)
    return get_arg(parser.parse_args()[arg_key], default, call_back)
