#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# __init__.py - 
#
# Author    :wangxinae(wangxinae@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd 
#
#
# *********************************************************************
# Change log:
#       - 2018/7/26 17:57  add by wangxinae
#
# *********************************************************************
import json
from copy import deepcopy

import requests

from library.basicfunction import assert_login, assert_login_out, default_testfile_path, file_export, file_import
from library.httpsession import http_session_admin, http_session_general_admin, http_session_user
from library.log import log
from library.private_status_codes import codes as dcn_codes
from library.utils import omit_long_data, str_eval


class SessionMethod(object):
    """Session Method"""

    def __init__(self, url, data, seq):
        """
        根据sheet表中传入的method，调用各个request方法。
        :param url: sheet表中对应测试点的url
        :param data: sheet表中对应测试点的data
        :param seq: sheet表中对应测试点的seq
        """
        self.url = url
        self.data = str_eval(data)
        self.seq = seq
        self.file_import_path = file_import(f'{self.url}{int(self.seq)}')
        self.file_export_path = file_export(f'{self.url}{int(self.seq)}')

    @staticmethod
    def safe_response_data(response):
        """
        安全的提取服务器response对象中json或者text内容
        :param response:
        :return:
        """
        try:
            response = response.json()
        except ValueError:
            response = omit_long_data(response.text)
        return response

    def display(self, response_json_or_text, method='POST'):
        """
        测试用例步骤输入输出显示
        :param method: http request method
        :param response_json_or_text: response json or text data
        :return:
        """
        msg = "\n[输入]:\n"
        msg += "> {method} {url}\n".format(method=method, url=self.url)
        if isinstance(response_json_or_text, dict):
            msg += "> kwargs: {kwargs}".format(kwargs=response_json_or_text.get('file') or self.data)
            dcn_raw_code = dcn_codes.get(response_json_or_text['status'])
            display_response = deepcopy(response_json_or_text)
            if dcn_raw_code:
                display_response['status'] = (display_response['status'], dcn_raw_code[0])
        else:
            display_response = response_json_or_text
        from pprint import pformat
        log(msg, level='info')
        log(f'\n[输出]:\n> response: {pformat(display_response)}', level='info')

    def post(self, session=http_session_admin):
        """
        函数做了判断，
            - 如果post请求中涉及到文件导入导出操作，需要提前打开文件。
            - 如果是用户登录登出，则走登录登出流程，
            - 其他就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        if self.file_import_path:
            file = {'file': open(default_testfile_path(self.file_import_path), 'rb')}
            j = session().post(self.url, files=file)
        elif assert_login(self.url):
            j = requests.post(self.url, json=self.data)
        elif assert_login_out(self.url):
            j = session().post(self.url)
        else:
            j = session().post(self.url, json=self.data)

        response = self.safe_response_data(j)
        if self.file_import_path and isinstance(response, dict):
            response['file'] = default_testfile_path(self.file_import_path)

        self.display(response)
        return response

    def post_user(self):
        """普通用户session保持"""
        return self.post(session=http_session_user)

    def post_admin(self):
        """通管理员session保持"""
        return self.post(session=http_session_general_admin)

    def post_no_login(self):
        """
        用于未登录用户相关测试
        :return: 返回post方法字典值
        """
        j = requests.post(self.url, json=self.data)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def get(self, session=http_session_admin):
        """
        用于超级管理员session保持
        函数做了判断，如果是需要导出的get方法，将get的内容到出到文件，如果不是，直接调用get方法
        :return: 返回get方法字典值
        """
        j = session().get(self.url, params=self.data)
        msg = f'\n=======content==========\n{j.content.decode(j.apparent_encoding)}'
        if self.file_export_path:
            with open(default_testfile_path(self.file_export_path), 'wb') as f:
                f.write(j.content)
            res = j.status_code
            self.display(msg, method='GET')
            response = {"status": res}
            return response
        else:
            response = self.safe_response_data(j)
            self.display(response, method='GET')
            return response

    def get_user(self):
        """
        普通用户session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        return self.get(session=http_session_user)

    def get_admin(self):
        """
        普通管理员session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        return self.get(session=http_session_general_admin)

    def get_no_login(self):
        """
        普通管理员session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        j = requests.get(self.url, params=self.data)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def put(self, session=http_session_admin):
        """
        :return: 返回字put方法典值
        """
        j = session().put(self.url, json=self.data)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def put_user(self):
        """
        :return: 返回字put方法典值
        """
        return self.put(session=http_session_user)

    def put_admin(self):
        """
        :return: 返回字put方法典值
        """
        return self.put(session=http_session_general_admin)

    def put_no_login(self):
        """
        :return: 返回字put方法典值
        """
        j = requests.get(self.url, json=self.data)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def delete(self, session=http_session_admin):
        """
        :return: 返回delete方法字典值
        """
        j = session().delete(self.url)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def delete_user(self):
        """
        :return: 返回delete方法字典值
        """
        return self.delete(session=http_session_user)

    def delete_admin(self):
        """
        :return: 返回delete方法字典值
        """
        return self.delete(session=http_session_general_admin)

    def delete_no_login(self):
        """
        :return: 返回delete方法字典值
        """
        j = requests.delete(self.url)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def head(self):
        """
        :return: 返回head方法字典值
        """
        j = http_session_admin().head(self.url)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def patch(self):
        """
        :return: 返回patch方法字典值
        """
        j = http_session_admin().patch(self.url, json=self.data)
        response = self.safe_response_data(j)
        self.display(response)
        return response

    def option(self):
        """
        :return: 返回option方法字典值
        """
        j = http_session_admin().options(self.url)
        response = self.safe_response_data(j)
        self.display(response)
        return response
