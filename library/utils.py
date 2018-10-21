#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# __init__.py - 
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
#       - 2018/4/13 12:51  add by yanwh
#
# *********************************************************************
import ast
import copy
import datetime
import os
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Callable

from library.log import log

GLOBAL_VARS_FILE_SAVE_PATH = Path(__file__).parent / '.pickle'


def display(*args, format_print=True, mode=None, log_level='info'):
    """
    打印输出到console和日志
    输入：display('dcn','test',format_print=True)
    输出：False
    ################################################################################
    # dcn
    # test
    ################################################################################
    输入：display('dcn','test',format_print=False)
    输出：dcn test
    `Required`
    :param mode: display模式默认为log输出,如果为print方式,指定mode='print'
    :param *args 显示到console/log文件的message
    `Optional`
    :param format_print:  是否统一格式化输出,默认为True
    :param log_level: 日志级别
    """
    output = (print_format(*args),) if format_print else (str(o) for o in args)
    if mode == 'print':
        print(*output)
    else:
        from .log import log
        log(*output, level=log_level)


def color(exclude=None):
    """
    Returns a random color for use in console display
    :param exclude: exclude colors
    :return:
    """
    try:
        import random
        colors = ['BLACK', 'BLUE', 'CYAN', 'GREEN', 'LIGHTBLACK_EX',
                  'LIGHTBLUE_EX', 'LIGHTCYAN_EX', 'LIGHTGREEN_EX',
                  'LIGHTMAGENTA_EX', 'LIGHTRED_EX', 'LIGHTWHITE_EX',
                  'LIGHTYELLOW_EX', 'MAGENTA', 'RED', 'RESET', 'WHITE', 'YELLOW']
        if exclude:
            assert isinstance(exclude, (str,)), '参数非String类型'
            if isinstance(exclude, (str,)) and exclude.upper() in colors:
                colors.remove(exclude.upper())
        return random.choice(colors)
    except Exception as e:
        from .log import log
        log("{} error: {}".format(color.__name__, str(e)))


def duration(start_time, stop_time):
    """
    函数作用：
    计算运行时间之差，并且以格式化为统一输出
    输入：datetime.datetime.now()
    输出：0Day,0:0:0(Hour:Min:Sec)
    最小精度为ms，预计时间精度初步达到要求，但是不够精细
    :param start_time:
    :param stop_time:
    :return: string
    """
    t = (stop_time - start_time)
    # 此处时间精度处理不够精确，体现在2点第一没有排除函数自身执行时间
    # 第二小数点后面精度不够（高精度使用decimal模块，配合getcontext）
    time_millisecond = t.microseconds / 1000
    time_hour = t.seconds // 60 // 60  # 此处注意python2和python3之间的区别，python2默认1/2=0，python3则为0.5（除非用此处floor除法）
    time_minute = (t.seconds - time_hour * 3600) // 60
    time_second = t.seconds - time_hour * 3600 - time_minute * 60
    return "%dDay,%d:%d:%d:%d(Hour:Min:Sec:Ms)" % (t.days, time_hour, time_minute, time_second, time_millisecond)


time_diff = duration  # 此处duration更具代表性


def print_timer(test_case_name, switch, *args, **kwargs):
    """
    (废弃?)
    测试例开始/结束计时
    :param test_case_name: 测试用例名称
    :param switch: 目前接受参数为：‘start’, ‘end’ 不区分大小写
    :param args: msg
    :param args: other args
    :return:
    """
    current_time = datetime.datetime.now()
    import re
    import pickle
    if re.fullmatch('(?i)start', switch):
        display(r'{title} {switch} {time}'.format(title=test_case_name, switch=switch, time=str(current_time)), *args,
                **kwargs)
        with open(GLOBAL_VARS_FILE_SAVE_PATH, 'wb+') as f:
            pickle.dump(current_time, f)
    elif re.fullmatch('(?i)end', switch):
        try:
            with open(GLOBAL_VARS_FILE_SAVE_PATH, 'rb+') as f:
                last_time = pickle.load(f)
        except (FileNotFoundError, Exception):
            last_time = None
        display(r'{title} {switch} {time}'.format(title=test_case_name, switch=switch, time=str(current_time)),
                'TestCase Duration Time:{time}'.format(
                    time=duration(last_time, current_time)) if last_time else ' ', *args, **kwargs)
    time.sleep(0.5)


@contextmanager
def print_timer_context(test_case_name, *args, **kwargs):
    """
    测试例开始/结束计时
    >>> with print_timer_context('hello, world') as doctest:
    ...    print(doctest)
    for doctest use

    :param test_case_name: 测试用例名称
    :param args: msg
    :param kwargs: other args
    :return:
    """
    start_time = datetime.datetime.now()
    try:
        log(r'{title} {switch} {time}'.format(title=test_case_name, switch='start at', time=str(start_time)),
            format_print=True, level='info', *args, **kwargs)
        yield 'for doctest use'
    finally:
        stop_time = datetime.datetime.now()
        log(r'{title} {switch} {time}'.format(title=test_case_name, switch='end at', time=str(stop_time)),
            'TestCase Duration Time:{time}'.format(time=duration(start_time, stop_time)),
            format_print=True, level='info', *args, **kwargs)


def print_check_case(sheet_name, result):
    """
    检查测试例step对错，打印并记录
    :param sheet_name: 测试用例sheet名称
    :param result: 测试结果列表
    """
    if 0 in result:  # 如果result列表中存在0表示测试用例失败
        log(f'{sheet_name} is FAILED!', result, level='error')
        r = False
    else:
        log(sheet_name + ' ' + 'is PASSED', level='info')
        r = True
    return r


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


def chinese_count(msg):
    """
    判断字符串中存在汉字的数量
    :param msg:
    :return: int
    """
    return [is_chinese(_s) for _s in msg].count(True)


def print_format(*msg):
    """
    打印标题日志格式
    add by yanwh 能够根据中文自动减少空格(英文占1个字符，中文占2个字符)
    TODO：一行输出太长之后能否自动换行，目前还无法识别中文，。等进行减少空格操作
    输入：print_format('test case','test for interface')
    输出：
    ################################################################################
    # test case                                                                    #
    # test for interface                                                           #
    ################################################################################
    :param msg: 输入需要输出的信息
    :return:
    """
    info = '\n' + '#' * 100
    line = '\n# '
    for j in msg:
        line += str(j)
        space = 100 - len(line) - chinese_count(line)
        if space > 0:
            line += ' ' * space
        line = line + '#'
        info += line
        line = '\n# '
    info += '\n' + '#' * 100
    return info


def status(timestamp):
    """
    函数作用：
    计算运行时间之差，并且以格式化为统一输出
    输入：time.time()
    :param float timestamp:   Unix timestamp (seconds since the Epoch)
    """
    import time
    c = time.time() - float(timestamp)
    data = ['{} days'.format(int(c / 86400.0)) if int(c / 86400.0) else str(),
            '{} hours'.format(int((c % 86400.0) / 3600.0)) if int((c % 86400.0) / 3600.0) else str(),
            '{} minutes'.format(int((c % 3600.0) / 60.0)) if int((c % 3600.0) / 60.0) else str(),
            '{} seconds'.format(int(c % 60.0)) if int(c % 60.0) else str()]
    return ', '.join([i for i in data if i])


def dict_merge(old, new):
    """
    字典递归合并
    """
    for key, value in old.items():
        if isinstance(value, dict):
            dict_merge(value, new[key])
        else:
            if key not in new:
                new[key] = value
    return new


def find_file(filename, raise_error_if_not_found=False, use_cwd=True):
    """
    如果use_cwd=True，会从当前路径依次从里到外递归查找filename，如果找到返回该文件存在路径，差找不到返回’‘
    如果use_cwd=False， 会从当前调用本函数的python模块所在路径开始从里到外递归查询文件，直到找到或者为’‘
    :param filename: 指定要查询文件，文件名称例如test.ini、1.py
    :param raise_error_if_not_found: 见名知意
    :param use_cwd: 见名知意
    :return: string or ’‘
    """

    def _walk_to_root(search_path):
        """
        Yield directories starting from the given directory up to the root
        """
        if not os.path.exists(search_path):  # pragma: no cover
            raise IOError('Starting search_path not found')

        if os.path.isfile(search_path):  # pragma: no cover
            search_path = os.path.dirname(search_path)

        last_dir = None
        current_dir = os.path.abspath(search_path)
        while last_dir != current_dir:
            yield current_dir
            parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
            last_dir, current_dir = current_dir, parent_dir

    if use_cwd or '__file__' not in globals():  # 支持在解释器中使用
        path = os.getcwd()
    else:
        import sys
        # noinspection PyProtectedMember
        frame_filename = sys._getframe().f_back.f_code.co_filename
        path = os.path.dirname(os.path.abspath(frame_filename))

    for dir_name in _walk_to_root(path):
        check_path = os.path.join(dir_name, filename)
        if os.path.exists(check_path):
            return check_path

    if raise_error_if_not_found:
        raise IOError('File not found')

    return ''


def doc_parametrize(**parameters) -> Callable:
    """
    Decorator for allowing parameters to be passed into docstring
    :param parameters: key value pair that corresponds to the params in docstring
    """

    def decorator_(callable_):
        new_doc = callable_.__doc__.format(**parameters)
        callable_.__doc__ = new_doc

        @wraps(callable_)
        def wrapper(*args, **kwargs):
            return callable_(*args, **kwargs)

        return wrapper

    return decorator_


def strip_blank_recursive(nested_list: list, evaluate: bool = False):
    """
    Strip blank space or newline characters recursively for a nested list
    *This updates the original list passed in*
    """
    if not isinstance(nested_list, list):
        raise ValueError(f"iterable passed must be type of list. not '{type(nested_list).__name__}'")

    for i, v in enumerate(nested_list):
        if isinstance(v, list):
            strip_blank_recursive(v, evaluate)
        elif isinstance(v, str):
            if not evaluate:
                val_ = v.strip()
            else:
                val_ = str_eval(v)

            nested_list[i] = val_


def str_eval(parse_str: str):
    """
    Evaluate string, return the respective object if evaluation is successful,
    """
    try:
        val = ast.literal_eval(parse_str.strip())
    except (ValueError, SyntaxError):  # SyntaxError raised when passing in "{asctime}::{message}"
        val = parse_str.strip()

    return val


def check_dict_conflict(source):
    """
    检查判断字典value是否存在冲突
    :param source:
    :return:
    """
    _check = {}
    for _k, _v in source.items():
        if _v in _check:
            err_msg = f'{_v}冲突 {_check[_v]}--->{_k}存在冲突键值对，请注意检查'
            log('存在冲突键值对，请注意检查', level='error')
            raise Exception(err_msg)
        _check[_v] = _k
