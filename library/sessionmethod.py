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
from pprint import pformat

import requests

from library.basicfunction import default_testfile_path, file_export, file_import, assert_login, \
    assert_login_out
from library.httpsession import http_session_user, http_session_admin, http_session_general_admin
from library.log import log


class SessionMethod(object):
    def __init__(self, url, data, seq):
        """
        根据sheet表中传入的method，调用各个request方法。
        :param url: sheet表中对应测试点的url
        :param data: sheet表中对应测试点的data
        :param seq: sheet表中对应测试点的seq
        """
        self.url = url
        self.data = data
        self.seq = seq

    def post(self):
        """
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果是用户登录登出，则走登录登出流程，其他就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        if file_import(self.url + str(int(self.seq))) is not None:
            file = {'file': open(default_testfile_path(file_import(self.url + str(int(self.seq)))), 'rb')}
            f = http_session_admin().post(self.url, files=file)
            log(file, level='info')
            log(f.json(), level='info')
            response = json.loads(f.text)
            return response
        elif assert_login(self.url) is not None:
            j = requests.post(self.url, data=json.dumps(eval(self.data)),
                              headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        elif assert_login_out(self.url) is not None:
            j = http_session_admin().post(self.url)
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        else:
            j = http_session_admin().post(self.url, data=json.dumps(eval(self.data)),
                                          headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response

    def post_user(self):
        """
        普通用户session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果是用户登录，则走登录流程，其他就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        if file_import(self.url + str(int(self.seq))) is not None:
            file = {'file': open(default_testfile_path(file_import(self.url + str(int(self.seq)))), 'rb')}
            f = http_session_user().post(self.url, files=file)
            log(file, level='info')
            log(f.text, level='info')
            response = json.loads(f.text)
            return response
        elif assert_login(self.url) is not None:
            j = requests.post(self.url, data=json.dumps(eval(self.data)),
                              headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        elif assert_login_out(self.url) is not None:
            j = http_session_user().post(self.url)
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        else:
            j = http_session_user().post(self.url, data=json.dumps(eval(self.data)),
                                         headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response

    def post_admin(self):
        """
        普通管理员session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果是用户登录，则走登录流程，其他就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        if file_import(self.url + str(int(self.seq))) is not None:
            file = {'file': open(default_testfile_path(file_import(self.url + str(int(self.seq)))), 'rb')}
            f = http_session_general_admin().post(self.url, files=file)
            log(file, level='info')
            log(f.json(), level='info')
            response = json.loads(f.text)
            return response
        elif assert_login(self.url) is not None:
            j = requests.post(self.url, data=json.dumps(eval(self.data)),
                              headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        elif assert_login_out(self.url) is not None:
            j = http_session_general_admin().post(self.url)
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response
        else:
            j = http_session_general_admin().post(self.url, data=json.dumps(eval(self.data)),
                                                  headers={'Content-Type': 'application/json;charset=UTF-8'})
            response = json.loads(j.text)
            log(j.json(), level='info')
            return response

    def post_no_login(self):
        """
        用于未登录用户相关测试
        :return: 返回post方法字典值
        """
        j = requests.post(self.url, data=json.dumps(eval(self.data)), headers={'Content-Type': 'application/json;charset=UTF-8'})
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def get(self):
        """
        用于超级管理员session保持
        函数做了判断，如果是需要导出的get方法，将get的内容到出到文件，如果不是，直接调用get方法
        :return: 返回get方法字典值
        """
        j = http_session_admin().get(self.url, params=self.data)
        log(f'\n=======content==========\n{j.content.decode(j.apparent_encoding)}', level='info')
        if file_export(self.url + str(int(self.seq))) is not None:
            f = open(default_testfile_path(file_export(self.url + str(int(self.seq)))), 'wb')
            f.write(j.content)
            f.close()
            res = j.status_code
            response = {"status": res}
            return response
        else:
            response = json.loads(j.text)
            return response

    def get_user(self):
        """
        普通用户session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        j = http_session_user().get(self.url, params=self.data)
        log(j.text, level='info')
        if file_export(self.url + str(int(self.seq))) is not None:
            f = open(default_testfile_path(file_export(self.url + str(int(self.seq)))), 'wb')
            f.write(j.content)
            f.close()
            res = j.status_code
            response = {"status": res}
            return response
        else:
            response = json.loads(j.text)
            return response

    def get_admin(self):
        """
        普通管理员session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        j = http_session_general_admin().get(self.url, params=self.data)
        log(f'\n=======message==========\n{j.content.decode(j.apparent_encoding)}', level='info')
        if file_export(self.url + str(int(self.seq))) is not None:
            f = open(default_testfile_path(file_export(self.url + str(int(self.seq)))), 'wb')
            f.write(j.content)
            f.close()
            res = j.status_code
            response = {"status": res}
            return response
        else:
            response = json.loads(j.text)
            return response

    def get_no_login(self):
        """
        普通管理员session保持
        函数做了判断，如果是需要导入的post方法，打开需要导入的文件并导入，如果不是，就根据sheet中data内容调用post方法
        :return: 返回post方法字典值
        """
        j = requests.get(self.url, params=self.data)
        log(j.json(), level='info')
        response = json.loads(j.text)
        return response

    def put(self):
        """
        :return: 返回字put方法典值
        """
        j = http_session_admin().put(self.url, data=json.dumps(eval(self.data)),
                                     headers={'Content-Type': 'application/json;charset=UTF-8'})
        log(json.dumps(eval(self.data)), level='info')
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def put_user(self):
        """
        :return: 返回字put方法典值
        """
        j = http_session_user().put(self.url, data=json.dumps(eval(self.data)),
                                    headers={'Content-Type': 'application/json;charset=UTF-8'})
        log(json.dumps(eval(self.data)), level='info')
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def put_admin(self):
        """
        :return: 返回字put方法典值
        """
        j = http_session_general_admin().put(self.url, data=json.dumps(eval(self.data)),
                                             headers={'Content-Type': 'application/json;charset=UTF-8'})
        log(json.dumps(eval(self.data)), level='info')
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def put_no_login(self):
        """
        :return: 返回字put方法典值
        """
        j = requests.put(self.url, data=json.dumps(eval(self.data)), headers={'Content-Type': 'application/json;charset=UTF-8'})
        log(json.dumps(eval(self.data)), level='info')
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def delete(self):
        """
        :return: 返回delete方法字典值
        """
        j = http_session_admin().delete(self.url)
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def delete_user(self):
        """
        :return: 返回delete方法字典值
        """
        j = http_session_user().delete(self.url)
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def delete_admin(self):
        """
        :return: 返回delete方法字典值
        """
        j = http_session_general_admin().delete(self.url)
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def delete_no_login(self):
        """
        :return: 返回delete方法字典值
        """
        j = requests.delete(self.url)
        response = json.loads(j.text)
        log(j.json(), level='info')
        return response

    def head(self):
        """
        :return: 返回head方法字典值
        """
        j = http_session_admin().head(self.url)
        response = json.loads(j.text)
        return response

    def patch(self):
        """
        :return: 返回patch方法字典值
        """
        j = http_session_admin().patch(self.url, data=json.dumps(eval(self.data)))
        response = json.loads(j.text)
        return response

    def option(self):
        """
        :return: 返回option方法字典值
        """
        j = http_session_admin().options(self.url)
        response = json.loads(j.text)
        return response
