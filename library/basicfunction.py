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
#       - 2018/8/17 14:57  add by wangxinae
#
# *********************************************************************

import re

from library.conf import settings


def default_testfile_path(testfile_name):
    """
    函数作用：动态获取导入导出文件路径
    :param testfile_name: 测试文件文件名称
    :return: csv的路径
    """
    return settings.as_path('DCN_TESTDATA_PATH') / 'testfile' / testfile_name


def file_export(url):
    """
    根据输入的url，判断需要导出的csv文件
    :param url: sheet表中读出的url
    :return: 导出的文件名
    """
    exports = settings.get('exports')  # 此处获取的exports为dict类型
    for key in exports:
        if re.match(key, url) is not None:
            return exports[key]  # 支持通过.的方式访问字典
    else:
        return None


def file_import(url):
    """
    根据输入的url，判断需要导入的csv文件
    :param url: sheet表中读出的url
    :return: 导出的文件名
    """
    imports = settings.get('imports')  # 将配置文件中的string转换成dict
    for key in imports:
        if re.match(key, url) is not None:
            return imports[key]
    else:
        return None


def assert_login(url):
    """
    函数作用：判断这个测试点是否是用户登录测试
    :param url: sheet表中读出的url
    :return: 返回这个url
    """
    if re.match(".+/user/login", url) is not None:
        return url
    else:
        return None


def assert_login_out(url):
    """
    函数作用：判断这个电视点是否是用户登出测试
    :param url: sheet表中读出的url
    :return: 返回这个url
    """
    if re.match(".+/user/logout", url) is not None:
        return url
    else:
        return None
