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
#       - 2018/8/13 10:32  add by wangxinae
#
# *********************************************************************
from interfacetest.projectsettings import project_settings


class HttpLogin(object):
    def __init__(self, seg_url='api/v1/user/login', username='admin', password='12345678'):
        """
         输入的用户名，密码用于后面创建会话，保持cookies
        :param seg_url: http登录url,默认值为'api/v1/user/login'
        :param username: http登录用户名，默认值为'admin'
        :param password: http登录密码 ，默认值为'12345678'
        """
        self.url = project_settings.base_url + seg_url
        self.username = username
        self.password = password

    @property
    def headers(self):
        """
        :return: http头信息
        """
        header = {
            # 'Content-Type': 'application/octet-stream;charset=UTF-8'
            'Content-Type': 'application/json;charset=UTF-8'
            # 'Content-Type': 'multipart/form-data'
        }
        return header

    def http_login(self):
        """
        :return: 返回一个session用于保持会话cookies
        """
        import json
        import requests
        session = requests.Session()
        data = {'account': self.username, 'password': self.password}
        session.post(self.url, data=json.dumps(data), headers=self.headers)
        return session


def http_session_admin():
    """
    :return: 用于管理员用户的会话保持
    """
    s = HttpLogin()
    http_session = s.http_login()
    return http_session


def http_session_user():
    """
    :return: 用于普通用户的会话保持
    """
    s = HttpLogin(username=project_settings.username1, password=project_settings.password1)
    http_session = s.http_login()
    return http_session


def http_session_general_admin():
    """
    :return: 用于普通管理员的会话保持
    """
    s = HttpLogin(username=project_settings.username4, password=project_settings.password4)
    http_session = s.http_login()
    return http_session
