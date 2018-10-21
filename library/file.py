#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# file.py - 
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
#       - 2018/9/29 8:48  add by yanwh
#
# *********************************************************************
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Pattern
import os

from library.log import log
from library.exceptions import InvalidOption, InvalidPathDir, InvalidPath, FileNotFound


def as_path(path_name):
    """
    将string类型路径转换成Path对象，同时解析成绝对路径，并且进行路径归一化，
    windows下文件名称非法字符为（\/:*?"<>|）抛出异常，记录日志
    :return:
    """
    try:
        if isinstance(path_name, Path):
            return path_name.resolve()
        return Path(path_name).resolve()
    except OSError as e:
        log(f'路径名称{path_name}含有如下非法字符（\/:*?"<>|）', level='error')
        raise InvalidPath from e


def assert_dir(dir_path):
    """
    探测dir_path是否为存在的有目录路径，如果不是返回InvalidPathDir异常
    :param dir_path:
    :return:
    """
    dir_path = as_path(dir_path)
    if not dir_path.is_dir():
        err_msg = f'{dir_path} 不是有效目录'
        log(err_msg, level='error')
        raise InvalidPathDir(err_msg)
    return dir_path


def assert_file(file_path):
    """
    探测file_path是否为存在的有效文件路径，如果不是返回FileNotFound异常
    :param file_path:
    :return:
    """
    file_path = as_path(file_path)
    if not file_path.is_file():
        err_msg = f'{file_path} 不是有效文件目录'
        log(err_msg, level='error')
        raise FileNotFound(err_msg)
    return file_path


def ensure_dir(dir_path, path_type='parent'):
    """
    确保指定路径文件的目录存在(不存在创建)
    :param dir_path: 需要确保的路径参数
    :param path_type: current or parent
    """
    path_mapping = {
        'current': as_path(dir_path),
        'parent': as_path(dir_path).parent
    }

    try:
        dir_abs = path_mapping[path_type]

        if not dir_abs.exists():
            msg = f'\n目标 -> {dir_path}\n创建 -> {dir_abs}'
            log(msg, level='info')
            dir_abs.mkdir(parents=True, exist_ok=True)
    except KeyError:
        err_msg = f"{path_type} 不是有效参数,有效参数为'parent' or 'current'"
        log(err_msg, level='error')
        raise InvalidOption(err_msg)


@contextmanager
def cd(dir_path: str):
    """
    Context manager for cd, change back to original directory when done
    """
    cwd = os.getcwd()
    try:
        os.chdir(os.path.expanduser(dir_path))
        yield
    finally:
        os.chdir(cwd)


def multiple_match(content, condition: [str, list, tuple, Pattern]):
    """
    尝试多种类型匹配，匹配成功返回True，失败返回False
    :param content: 被匹配的内容
    :param condition: 用于匹配的Pattern
    注意：如果传入list或者tuple递归判断，condition（list）中的任一元素便算返回成功
    :return:True or False
    >>> multiple_match(1,1)
    True
    >>> multiple_match(1,12)
    False
    >>> multiple_match(1,123)
    False
    >>> multiple_match(1,'123')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "<input>", line 10, in multiple_match
      File "C:\Python36\lib\re.py", line 172, in match
        return _compile(pattern, flags).match(string)
    TypeError: expected string or bytes-like object
    >>> multiple_match('1','^123')
    False
    >>> multiple_match('123','^1')
    True
    >>> multiple_match('123','23')
    False
    >>> multiple_match('123','111')
    False
    >>> p=re.match('_test.*')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
    TypeError: match() missing 1 required positional argument: 'string'
    >>> p=re.compile('_test.*')
    >>> multiple_match('_test 1',p)
    True
    >>> multiple_match('_te st 1',p)
    False
    >>> multiple_match('testcase',['test', 123, 'test111'])
    True
    >>> multiple_match('testcase',['test123', 123, 'test456'])
    False
    >>> multiple_match('testcase',[123, '123', 'test111'])
    False
    """
    result = []
    if isinstance(condition, str):
        return True if re.match(condition, content) else False
    elif isinstance(condition, Pattern):
        return True if condition.match(content) else False
    elif isinstance(condition, (list, tuple)):
        for sub_condition in condition:
            result.append(multiple_match(content, sub_condition))
        return True if any(result) else False
    else:
        return content == condition


def scan_depth_dir(scan_path: [str, os.PathLike], depth: int, condition: [str, list, tuple, Pattern] = False):
    """
    用于获取scan_path下面递归深度在depth并且满足condition的文件夹,
    跟scan_dir重要区别如果目录结构如下
    E:
        -wireless
            -test
            -interface
                -test
    p=scan_depth_dir('E:\wireless', condition='test.*',depth=5)
    p1=scan_dir('E:\wireless', condition='test.*')
    p只会匹配 E:\wireless\test
    p1除了会匹配E:\wireless\test，还会匹配E:\wireless\interface\test
    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤
    :param depth: 递归扫描深度,以scan_path为基础向下扫描2个目录
    :param scan_path: 扫描起始路径，默认只扫描起始目录下一层目录（就这样吧）
    :return: dict {文件名：WindowsPath(文件名对应全路径)}
    usage:
    目录如下
        +
    dir
        sub_dir
            sub_dir_1
                sub_dir_11
                    sub_file_11
                .sub_dir_1
                    __sub_file_1
            sub_dir_2
                sub_file_2
        __sub_dir
            +testcase
                +library
    运行 scan_valid_dir(r'dir/', condition=r'[A-Za-z]+', dept=2))
    {
    'dir>sub_dir_sub_dir_1'：'dir/sub_dir_1'，
    'sub_dir_2': 'dir/sub_dir_2'
    }
        运行 scan_valid_dir(r'dir/', condition=r'[A-Za-z]+', dept=3))
    {
    WindowsPath('dir/sub_dir_1')：'dir/sub_dir_1'，
    WindowsPath('dir/sub_dir_2'): 'dir/sub_dir_2'
    WindowsPath('dir/sub_dir_1/sub_dir_11')：'dir/sub_dir_1/sub_dir_11'，
    }
    """
    scan_path = assert_dir(scan_path)

    if depth <= 0:
        return
    for sub_obj in scan_path.iterdir():
        if sub_obj.is_dir():
            if condition and multiple_match(sub_obj.stem, condition) is False:
                continue
            else:
                yield sub_obj
            yield from scan_depth_dir(scan_path / sub_obj.stem, depth - 1, condition)  # 递归遍历


def scan_dir(scan_path: [str, os.PathLike], condition: [str, list, tuple, bool, Pattern] = False, **kwargs):
    """
    用于获取scan_path下面所有满足condition的文件夹

    :param scan_path: 扫描起始路径
    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤
    :param kwargs: 附加参数参考 topdown=True, onerror=None, followlinks=False用法参照os.walk
    :return:
    """
    assert_dir(scan_path)

    for dir_path, dir_names, file_names in os.walk(scan_path, **kwargs):
        for dir_name in dir_names:
            if condition and multiple_match(dir_name, condition) is False:
                continue
            else:
                yield as_path(dir_path) / dir_name


def scan_file(scan_path: [str, os.PathLike], condition: [str, list, tuple, bool, Pattern] = False, **kwargs):
    """
    用于获取scan_path下面所有满足condition的文件

    :param scan_path: 扫描起始路径
    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤
    :param kwargs: 附加参数参考 topdown=True, onerror=None, followlinks=False用法参照os.walk
    :return:
    """
    assert_dir(scan_path)

    for dir_path, dir_names, file_names in os.walk(scan_path, **kwargs):
        for filename in file_names:
            if condition and multiple_match(filename, condition) is False:
                continue
            else:
                name, _, _ = filename.rpartition('.')
                yield as_path(dir_path) / filename


class FileReader(object):
    """
    记住文件上次读取的位置，从后面接着读取，例如实例化FileReader之后执行read， max_read_size=100，之后
    继续读取的时候会从100之后接着读取后面内容
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.pos = 0

    # noinspection PyNoneFunctionAssignment
    def read(self, max_read_size=None):
        """
        从上一次读取的位置继续读取
        :param max_read_size:
            一次读取的最大长度
        :return:
            读取的文件内容
        """
        import os
        if not os.path.isfile(self.file_path):
            return ""
        with open(self.file_path) as fp:
            size = fp.seek(0, os.SEEK_END)
            if size >= self.pos:
                fp.seek(self.pos, os.SEEK_SET)
                if (max_read_size is None) or (max_read_size > (size - self.pos)):
                    max_read_size = size - self.pos
                ret = fp.read(max_read_size)
                self.pos = self.pos + len(ret)
            else:  # may be a new file with the same name
                fp.seek(0, os.SEEK_SET)
                if (max_read_size is None) or (max_read_size > size):
                    max_read_size = size
                ret = fp.read(max_read_size)
                self.pos = len(ret)
        return ret
