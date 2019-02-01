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
"""
+ 模块说明：
    file模块提供跟文件目录相关的类和函数，用户文件路径查找

"""
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Pattern, List, Tuple
import os

from library.log import log
from library.exceptions import InvalidOption, InvalidPathDir, InvalidPath, FileNotFound


def as_path(path_name):
    """
    + 说明:
        1. string类型或者Path实例路径进行格式化和统一化，如果是string转换成Path实例,
        2. Path实例解析成绝对路径,
        3. string中存在 windows下文件名称非法字符为抛出异常，记录日志。

    >>> as_path('E:/1/2/3')
    WindowsPath('E:/1/2/3')
    >>> as_path('E:/1')
    WindowsPath('E:/1')

    :param path_name: 文件路径名称（string）/WindowPath实例。
    :return: WindowsPath实例。

    """
    try:
        if isinstance(path_name, Path):
            return path_name.resolve()
        return Path(path_name).resolve()
    except OSError as e:
        err_msg = f'路径名称{path_name}含有如下非法字符（\/:*?"<>|）'
        log(err_msg, level='error')
        raise InvalidPath(err_msg) from e


def assert_dir(dir_path):
    """
    + 说明：
        探测dir_path是否为存在的有目录路径，如果不是返回InvalidPathDir异常。

    :param dir_path: 文件目录路径名称（string）/WindowPath实例。
    :return: WindowsPath实例
    """
    dir_path = as_path(dir_path)
    if not dir_path.is_dir():
        err_msg = f'{dir_path} 不是有效目录'
        log(err_msg, level='error')
        raise InvalidPathDir(err_msg)
    return dir_path


def assert_file(file_path):
    """
    + 说明：
        测file_path是否为存在的有效文件路径，如果不是返回FileNotFound异常。

    :param file_path: 文件路径名称（string）/WindowPath实例。
    :return: WindowsPath instance
    """
    file_path = as_path(file_path)
    if not file_path.is_file():
        err_msg = f'{file_path} 不是有效文件目录'
        log(err_msg, level='error')
        raise FileNotFound(err_msg)
    return file_path


def ensure_dir(dir_path, path_type='parent'):
    """
    + 说明：
        确保指定路径文件的目录存在(不存在创建)。

    :param dir_path: 需要确保的路径参数。
    :param path_type: current或者parent。
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
    + 说明：
        应用场景为程序执行到某个地方想跑到某个目录下面执行相关命令或者操作，
        执行完毕之后需要返回原来路径继续进行操作。利用上下文管理器实现该特性。
    """
    cwd = os.getcwd()
    try:
        os.chdir(os.path.expanduser(dir_path))
        yield
    finally:
        os.chdir(cwd)


def multiple_match(content, condition: [str, List, Tuple, Pattern]):
    """
    + 说明：
        尝试多种类型匹配，匹配成功返回True，失败返回False
    + 注意：
        如果传入list或者tuple递归判断，condition（list）中的任一元素便算返回成功

    :param content: 被匹配的内容
    :param condition: 用于匹配的Pattern
    :return: True or False

    >>> multiple_match(1,1)
    True
    >>> multiple_match(1,12)
    False
    >>> multiple_match(1,123)
    False
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
    + 说明:
        用于获取scan_path下面递归深度在depth并且满足condition的文件夹。

    + 注意：
        目录结构(跟scan_dir函数有区别)

        >>> wireless
        >>>    test
        >>>    interface
        >>>        test

        scan_depth_dir = scan_depth_dir('/wireless', condition='test.*')

        scan_dir = scan_dir('/wireless', condition='test.*')

        scan_depth_dir只会匹配 /wireless/test.

        scan_dir除了会匹配E:/wireless/test，还会匹配/wireless/interface/test.

    + 用法：
        目录结构

        dir
            sub_dir
                sub_dir_1
                    sub_dir_11
                        sub_file_11
                    sub_dir_1
                        __sub_file_1
                sub_dir_2
                    sub_file_2
            __sub_dir
                testcase
                    library

        运行 scan_valid_dir(r'dir/', condition=r'[A-Za-z]+', dept=2))

            {

            'dir>sub_dir_sub_dir_1'：'dir/sub_dir_1'，

            'sub_dir_2': 'dir/sub_dir_2'

            }

        运行 scan_valid_dir(r'dir/', condition=r'[A-Za-z]+', dept=3))

            {

            WindowsPath('dir/sub_dir_1')：'dir/sub_dir_1'，

            WindowsPath('dir/sub_dir_2'): 'dir/sub_dir_2'，

            WindowsPath('dir/sub_dir_1/sub_dir_11')：'dir/sub_dir_1/sub_dir_11'

            }

    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤
    :param depth: 递归扫描深度,以scan_path为基础向下扫描2个目录
    :param scan_path: 扫描起始路径，默认只扫描起始目录下一层目录（就这样吧）
    :return: { 文件名：WindowsPath(文件名对应全路径) }

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
    + 说明：
        用于获取scan_path下面所有满足condition的文件夹。

    :param scan_path: 扫描起始路径。
    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤。
    :param kwargs: 附加参数参考 topdown=True, onerror=None, followlinks=False用法参照os.walk。
    :return: 文件夹路径。
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
    + 说明：
        用于获取scan_path下面所有满足condition的文件路径。

    :param scan_path: 扫描起始路径
    :param condition: 正则表达式，用于文件夹名称的过滤,string类型，或者正则表达式Pattern类型,如果传入值为None，'' [] False 表示不过滤。
    :param kwargs: 附加参数参考 topdown=True, onerror=None, followlinks=False用法参照os.walk
    :return: 生成器表达式。

    """
    assert_dir(scan_path)

    for dir_path, dir_names, file_names in os.walk(scan_path, **kwargs):
        for filename in file_names:
            if condition and multiple_match(filename, condition) is False:
                continue
            else:
                name, _, _ = filename.rpartition('.')
                yield as_path(dir_path) / filename


# noinspection PyTypeChecker
class FileReader(object):
    """
    + 说明：
        FileReader主要作用用于实例化对象在读取文件的时候可以按照指定的长度读取指定的内容，后面根据需要用该实例再次读取文件
        的时候可以从上次读取的位置接着向后读取，假设有一种应用场景需要读取文件内容非常大，一次读取到内存可能吃不消，如果用yield
        返回又不能一次读取一块内容，yield只能一次返回单个内容。
    + 举例：
        实例化FileReader之后执行read， max_read_size=100，之后继续读取的时候会从100之后接着读取后面内容。

    """

    def __init__(self, file_path):
        """
        需要读取的文件路径

        :param file_path: 需要读取的文件路径
        """
        self.file_path = file_path
        self.pos = 0

    # noinspection PyNoneFunctionAssignment
    def read(self, max_read_size=None):
        """
        + 说明：
            如果max_read_size=None，一次读完全部文件，否则按照max_read_size值读取指定长度文件内容
            再次调用read会从上一次读取的位置接着往后面读max_read_size的文件内容

        :param max_read_size: 读取文件内容的最大长度
        :return: max_read_size长度的内容
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
