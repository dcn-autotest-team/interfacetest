#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# global_settings.py - 
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
#       - 2018/10/9 11:04  add by yanwh
#
# *********************************************************************
import logging
from enum import Enum, unique
from colorama import Fore


DCN = """
██████╗  ██████╗███╗   ██╗
██╔══██╗██╔════╝████╗  ██║
██║  ██║██║     ██╔██╗ ██║
██║  ██║██║     ██║╚██╗██║
██████╔╝╚██████╗██║ ╚████║   
╚═════╝  ╚═════╝╚═╝  ╚═══╝ 
"""
# ----------------库默认常量------------------------------------------------------------
TITLE = '公共库函数'
DESCRIPTION = 'DC云科自动化组公共库函数'
VERSION = '1.0.2'
BUILD = 0x010002
LICENSE = 'MIT'
COPYRIGHT = 'Copyright 2018 DCN'
AUTHOR = ['wangxinae', 'yanwh']
AUTHOR_EMAIL = ['wangxinae@digitalchina.com', 'yanwh@digitalchina.com']
CAKE = u'\u2728 \U0001f370 \u2728'
ENCODING = 'utf-8'
# ----------------log.py模块常量--------------------------------------------------------
# default logger的名称
DEFAULT_LOGGER = "default"

# 所有默认内部logger均带有此属性名称
INTERNAL_LOGGER_ATTR = "internal"

# 用于标记handler是否有custom loglevel
INTERNAL_CUSTOM_LOGLEVEL = "internal_handler_custom_loglevel"

# DEFAULT_FORMAT/DEFAULT_DATE_FORMAT/DEFAULT_COLORS 用于log.py下面的LogFormatter类
# 用于指定默认日志(logger)-->默认Formatter的默认格式,决定日志最终格式
DEFAULT_FORMAT = '[%(levelname)1.1s %(asctime)s] %(color)s%(message)s%(end_color)s'
# '[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(color)s%(message)s%(end_color)s'
# 用于指定默认日志默认Formatter的默认日期格式
DEFAULT_DATE_FORMAT = '%y年%m月%d日 %H时%M分%S秒'
# 例如2018年09月30日 15时52分41秒514毫秒

# 默认显示为 180930 14:18:29
# 用于指定不同log级别的日志颜色
LOGLEVEL_COLOR_OPTS = {
    logging.CRITICAL: Fore.LIGHTRED_EX,
    logging.ERROR: Fore.RED,
    logging.WARNING: Fore.YELLOW,
    logging.WARN: Fore.YELLOW,
    logging.INFO: Fore.GREEN,
    logging.DEBUG: Fore.LIGHTBLUE_EX,
    logging.NOTSET: Fore.WHITE,
}


# --------------自定义unittest模块常量-----------------------------------------------------------------------


@unique
class Tag(Enum):
    SMOKE = 1  # 冒烟测试标记，可以重命名，但是不要删除
    FULL = 1000  # 完整测试标记，可以重命名，但是不要删除

    # 以下开始为扩展标签，自行调整
    SP = 2

# 只运行用例类型
RUN_CASE = {Tag.SMOKE}

# 开启用例排序
SORT_CASE = True

# 每个用例的执行间隔，单位是秒
EXECUTE_INTERVAL = 0.1
# 开启检测用例描述
CHECK_CASE_DOC = True

# 显示完整用例名字（函数名字+参数信息）
FULL_CASE_NAME = False

# 测试报告显示的用例名字最大程度
MAX_CASE_NAME_LEN = 80

# 执行用例的时候，显示报错信息
SHOW_ERROR_TRACEBACK = True

# 生成ztest风格的报告
CREATE_ZTEST_STYLE_REPORT = True

# 生成bstest风格的报告
CREATE_BSTEST_STYLE_REPORT = False
