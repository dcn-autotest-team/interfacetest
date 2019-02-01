#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# core.py
#
# Author    :yanwh(yanwh@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd
#
#
# *********************************************************************
# Change log:
#       - 2019/1/28 16:26  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
import inspect
from functools import wraps
from typing import ByteString

from jinja2 import Template
from pithy import JSONProcessor
from pithy.api import HttpRequest, Request
from pithy.utils import format_json
from requests.sessions import Session

from library.log import log


class PrivateHttpRequest(HttpRequest):
    """
    自定义Http Request
    """

    def __init__(self, url='', method='get', **kwargs):
        super(PrivateHttpRequest, self).__init__(url, method, **kwargs)

    def create_session(self):
        """
        如果接收到的要变参数中有session,且为Session对象,赋值给session变量, 否则创建一个
        """
        if self.is_class:
            self.session = getattr(self.func_im_self, 'session', None)
            if not isinstance(self.session, Session):
                session = Session()
                setattr(self.func_im_self, 'session', session)
                self.session = session

        elif isinstance(self.func_return.get('session'), Session):
            self.session = self.func_return.get('session')
        else:
            self.session = Session()

    def __call__(self, func):
        self.func = func
        self.is_class = False
        try:
            if inspect.getargspec(func).args[0] == 'self':
                self.is_class = True
        except IndexError:
            pass

        def fun_wrapper(*args, **kwargs):
            output = kwargs.pop('output') if kwargs.get('output') else False
            self.func_return = self.func(*args, **kwargs) or {}
            self.func_im_self = args[0] if self.is_class else object

            try:
                self.func.__doc__ = self.func.__doc__.decode('utf-8')
            except:
                pass
            self.func_doc = (self.func.__doc__ or self.func.__name__).strip()
            self.create_url()
            self.create_session()
            self.session.headers.update(getattr(self.func_im_self, 'headers', {}))
            self.decorator_args.update(self.func_return)
            return PrivateRequest(self.method, self.url, self.session, self.func_doc, self.decorator_args,
                                  output=output)

        return fun_wrapper


session = Session()
request = PrivateHttpRequest

LOG_TEMPLATE = """
******************************************************
{% for index, item in items %}
{{ index + 1 }}、{{ item['desc'] }}
{{ item['value'] }}
{% endfor %}
'''"""


def private_context(func):
    def wrapper(self):
        self._request()
        try:
            res = func(self)
        finally:
            if self.output:
                self._log()
        return res

    return wrapper


class PrivateJSONProcessor(JSONProcessor):
    """python3新版本中__str__方法无法返回byte type报错"""

    def __str__(self):
        format_json_data = format_json(self)
        if isinstance(format_json_data, ByteString):
            format_json_data = format_json(self).decode('utf-8')
        return format_json_data


def status_code_mapping(resp_json):
    """
    将接口返回的状态码转换成对应的名称，例如：0在接口文档描述中表述为此次操作成功 0 ->'操作成功'
    :param resp_json: 要转换的json字符串
    :return: 转换后的json字符串
    """
    from copy import deepcopy
    change_resp_json = deepcopy(resp_json)
    from library.private_status_codes import codes as dcn_codes
    dcn_raw_code = dcn_codes.get(resp_json['status'])
    if dcn_raw_code:
        change_resp_json['status'] = f"{resp_json['status']}({dcn_raw_code[0]})"
    return change_resp_json


class PrivateRequest(Request):
    """
     自定义Request
    """

    def __init__(self, *args, **kwargs):
        self.output = kwargs.pop('output')
        super(PrivateRequest, self).__init__(*args, **kwargs)

    def _log(self):
        log(Template(LOG_TEMPLATE).render(items=enumerate(self.log_content)))

    @private_context
    def to_json(self):
        """change to json"""
        try:
            response_json = self.response.json()
            self.log_content.append(dict(
                desc=u'响应结果',
                value=format_json(status_code_mapping(response_json))
            ))
        except ValueError:
            self.log_content.append(dict(
                desc=u'响应结果',
                value=self.response.content.decode('utf-8')
            ))
            raise ValueError(u'No JSON object in response')

        return PrivateJSONProcessor(response_json)

    @private_context
    def to_content(self):
        response_content = self.response.content
        self.log_content.append(dict(desc=u'响应结果', value=response_content.decode('utf-8')))
        return response_content

    def __getattr__(self, item):
        self._request()
        if self.output:
            self._log()
        return getattr(self.response, item)


def optional_output(func):
    """
    根据调用方式有选择性的打印输出
    :param func:
    :return:
    """
    if 'output' in inspect.getargspec(func).args:
        raise TypeError('output argument already defined')

    @wraps(func)
    def wrapper(*args, output=False, **kwargs):
        if output:
            return func(*args, output=output, **kwargs)
        return func(*args, **kwargs)

    return wrapper
