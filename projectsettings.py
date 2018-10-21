#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# projectsettings.py - 
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
#       - 2018/9/26 20:40  add by yanwh
#
# *********************************************************************
import os

from library.conf import settings
from library.file import scan_depth_dir, scan_file
from library.loader import load_file
from library.log import log, log_instance


def setup_project(start_path=os.getcwd()):
    """
    从指定起始路径扫描指定后缀配置文件
    :param start_path: 默认值为当前根路径
    :return: None
    """
    def parse_conf(conf_file_path):
        log(f'开始从{conf_file_path}中解析配置文件')
        _config = load_file(conf_file_path)
        for key, value in _config.items():
            if conf_file_path.suffix == '.ini':
                for sub_key, sub_value in value.items():
                    settings.set(sub_key, sub_value)
            else:
                settings.set(key, value)  # 解析json？？或者其他配置文件

    log(f'开始从{start_path}扫描...', level='debug')
    # 扫描当前项目文件夹，根据项目需求只扫描外面2层目录即可，正则过滤无效的.或者__打头的隐藏或者无效目录
    target_dir = scan_depth_dir(start_path, depth=2, condition='[A-Za-z]+')
    for dir_path in target_dir:  # 魔改目录名称
        settings.set(f"DCN_{dir_path.stem.upper()}_PATH", dir_path)
    # 扫描当前项目config中的ini配置文件(目前只扫描ini/json文件,后续可以进行扩展)
    target_conf_path = scan_file(settings.get('DCN_CONFIG_PATH'), condition=('[\w]+\.ini', '[\w]+\.json'))
    for conf in target_conf_path:
        parse_conf(conf)
    # 扫描当前项目testdata中的xls和xlsx的文件，正则排除以~$开头的临时文件
    target_file = scan_file(settings.get('DCN_TESTDATA_PATH'), condition=('[\w]+\.xls', '[\w]+\.xlsx'))
    for _file in target_file:
        settings.set(_file.stem, _file)

    def modify_log_report_config():
        """
        根据项目实际需要修改log和report目录，存放结构如下
        test_report/current_time/console.log
        test_report/current_time/report.html
        :return: None
        """
        import time
        current_time = time.strftime("%Y%m%d%H%M%S")
        if settings.get('report_file_modify'):  # 根据配置文件中的策略修改日志和报告路径
            report_path = settings.get('DCN_TESTREPORT_PATH')
            settings.set('report_dir_path', (report_path / current_time).__fspath__())
            settings.set('report_file', (report_path / current_time / settings.get('report_name')).__fspath__())
            if settings.log_file_modify:
                settings.set('log_dir_path', (report_path / current_time).__fspath__())
                settings.set('log_file', (report_path / current_time / settings.get('log_name')).__fspath__())
        del time

    modify_log_report_config()  # 动态修改日志和报告存放路径和信息
    import sys
    sys.modules['library.conf'].settings = settings


def setup_unittest():
    """run_case比较特殊需要将其转换成Enum类型"""
    settings.set('RUN_CASE', eval(settings.RUN_CASE, {'Tag': settings.Tag}))
    # 将配置文件中字符串转换成Tag类型


def setup_log():
    log_instance.logger = log_instance.setup(
        name=settings.logger_name,
        log_file=settings.log_file if settings.file_log_on else None,  # 用于判断是否生成日志文件
        console_level=settings.log_level_in_console,
        fmt=settings.log_fmt,
        max_bytes=settings.max_bytes_each,
        backup_count=settings.backup_count,
        logfile_level=settings.log_level_in_logfile,
        display_to_console=settings.console_log_on,
    )
    log('根据项目ini文件重新设置日志默认格式')


def setup():
    log('项目初始化环境设置中...')
    # 动态扫描整个项目目录，读取配置文件中的ini文件
    setup_project()
    # 动态读取配置文件中日志配置

    setup_log()

    # 动态读取配置文件中unittest配置
    setup_unittest()

    log('项目初始化完成...', color='yellow')

project_settings = settings
