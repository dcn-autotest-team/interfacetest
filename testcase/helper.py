#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# helper.py - 
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
#       - 2018/9/6 20:39  add by yanwh
#
# *********************************************************************
import os
from functools import wraps

import sys

try:
    from mysql.connector import connect  # mysql不好安装建议换成pymysql
except ImportError:
    from pymysql import connect

from library.conf import settings
from library.apitest import Api
from library.exceptions import FrameNotFound
from library.utils import print_check_case


def modname(back=0):
    """
    获取模块名称,获取逻辑为从调用栈中获取调用run装饰器的python文件，返回处理之后的文件名称，否则获取当前python文件名称传入
    :return: string
    """
    from inspect import getmodulename, getfile, currentframe
    _cur_frame = currentframe()

    try:
        # _caller_frame = _cur_frame.f_back.f_back
        _caller_frame = sys._getframe(back + 1)
        if _cur_frame and _caller_frame:
            module_name = getfile(_caller_frame)
            return os.path.splitext(os.path.basename(module_name))[0] if os.path.isfile(module_name) \
                else getmodulename(__file__)
    except:
        raise FrameNotFound


def run():
    from inspect import isclass

    def decorate(func):
        file_name = getattr(settings, modname(1))

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            mapping_name = f'{os.path.splitext(os.path.basename(file_name))[0]}_{func_name}'
            sheet_name = getattr(settings, mapping_name)
            res = print_check_case(sheet_name, Api(file_name, sheet_name)
                                   .api())

            if func_name == 'test_uninitiated':
                modify_autoincrement(2)
            if func_name == 'tearDownClass':
                modify_autoincrement(6)
            if isclass(args[0]):
                # 判断返回的是一个类还是一个实例，对返回是类和实例的情况分别进行处理
                args[0]().assertTrue(res)
                # try:
                #     args[0]().assertFalse(res)
                # except:
                #     pass
            else:
                args[0].assertTrue(res)
            return func(*args, **kwargs)

        return wrapper

    return decorate


def connect_db(table_name, num):
    """

    :param table_name: 表名
    :param num:表的auto_increment值
    :return:
    """
    sql = f"ALTER TABLE {table_name} AUTO_INCREMENT={num}"
    from contextlib import closing
    with closing(connect(**settings.config)) as conn, \
            closing(conn.cursor(buffered=True)) as cur:
        cur.execute(sql)


def modify_autoincrement(num, user="tbl_user", org="tlb_organization", group="tlb_user_group"):
    connect_db(user, num)
    connect_db(org, num)
    connect_db(group, settings.autoincrement + 1)
