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
"""
    + 模块说明：
        常用工具集
"""
import ast
import copy
import datetime
import os
import re
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Callable

from library.exceptions import ParamsError
from library.log import log

GLOBAL_VARS_FILE_SAVE_PATH = Path(__file__).parent / '.pickle'


def omit_long_data(body, omit_len=512):
    """ omit too long str/bytes
    """
    if not isinstance(body, str):
        return body

    body_len = len(body)
    if body_len <= omit_len:
        return body

    omitted_body = body[0:omit_len]

    appendix_str = " ... OMITTED {} CHARACTORS ...".format(body_len - omit_len)
    if isinstance(body, bytes):
        appendix_str = appendix_str.encode("utf-8")

    return omitted_body + appendix_str


def lower_dict_keys(origin_dict):
    """ convert keys in dict to lower case

    Args:
        origin_dict (dict): mapping data structure

    Returns:
        dict: mapping with all keys lowered.

    Examples:
        >>> origin_dict = {
            "Name": "",
            "Request": "",
            "URL": "",
            "METHOD": "",
            "Headers": "",
            "Data": ""
        }
        >>> lower_dict_keys(origin_dict)
            {
                "name": "",
                "request": "",
                "url": "",
                "method": "",
                "headers": "",
                "data": ""
            }

    """
    if not origin_dict or not isinstance(origin_dict, dict):
        return origin_dict

    return {
        key.lower(): value
        for key, value in origin_dict.items()
    }


def build_url(base_url, path):
    """ prepend url with hostname unless it's already an absolute URL """
    absolute_http_url_regexp = re.compile(r"^https?://", re.I)
    if absolute_http_url_regexp.match(path):
        return path
    elif base_url:
        return "{}/{}".format(base_url.rstrip("/"), path.lstrip("/"))
    else:
        raise ParamsError("base url missed!")


def wait_object_property(obj: object, property_name: str, waited_value: str,
                         timeout: [int, float] = 10, interval: [int, float] = 0.5, regular_match: bool = False):
    """
    + 说明：
        通过比较obj.property_name和waited_value，等待属性值出现。
        如果属性值obj.property_name是字符类型则waited_value做为正则表达式进行比较。
        比较成功则返回，超时则抛出TimeoutError异常。
    + 场景：
        Dauto平台上面，经常打开串口的时候获取不到类属性导致后面操作异常，
        此处可以使用改函数作为实际应用场景。

    :param obj: 要等待的实例或者类对象
    :param interval: 尝试时间间隔
    :param timeout: 尝试超时总时长
    :param property_name: 要等待的obj对象的属性名
    :param waited_value: 要比较的的属性值，支持多层属性
    :param regular_match: 参数 property_name和waited_value是否采用正则表达式的比较。默认为不采用（False）正则，而是采用恒等比较
    """
    start = time.time()
    try_count = 0
    is_str = isinstance(waited_value, str)
    while 1:
        temp_obj = obj  # 增加多层属性支持，例如a.b.c.e
        property_names = property_name.split('.')
        for i in range(len(property_names)):
            prop_value = getattr(temp_obj, property_names[i])
            temp_obj = prop_value

        if is_str and regular_match:
            if re.search(waited_value, prop_value):
                break
        else:
            if waited_value == prop_value:
                break
        try_count += 1
        waited = time.time() - start
        if waited < timeout:
            time.sleep(min(interval, timeout - waited))
        else:
            raise TimeoutError("对象属性值比较超时（%d秒%d次）：期望值:%s，实际值:%s，"
                               % (timeout, try_count, waited_value, prop_value))


def display(*args, format_print=True, mode=None, log_level='info'):
    """
    + 说明:
        打印输出到console和日志

    + 用法:
        输入：display('dcn','test',format_print=True)

        输出：False

        >>> ################################################################################
        >>> # dcn                                                                          #
        >>> # test                                                                         #
        >>> ################################################################################

        输入：display('dcn','test',format_print=False)

        输出：dcn test

    :param mode: display模式默认为log输出,如果为print方式,指定mode='print'
    :param args: 显示到console/log文件的message
    :param format_print: 是否统一格式化输出,默认为True
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
    + 说明：
        在串口返回随机颜色字符串，随机范围如下（可以通过exclude缩小随机范围）

        {

        'BLACK', 'BLUE', 'CYAN', 'GREEN', 'LIGHTBLACK_EX',
        'LIGHTBLUE_EX', 'LIGHTCYAN_EX', 'LIGHTGREEN_EX',
        'LIGHTMAGENTA_EX', 'LIGHTRED_EX', 'LIGHTWHITE_EX',
        'LIGHTYELLOW_EX', 'MAGENTA', 'RED', 'RESET', 'WHITE', 'YELLOW'

        }

    :param exclude: 随机颜色中排除指定颜色
    :return: 颜色字符串
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
    + 说明：
        计算运行时间之差，并且以格式化为统一输出
        输入：datetime.datetime.now()
        输出：0Day,0:0:0(Hour:Min:Sec)
        最小精度为ms，预计时间精度初步达到要求，但是不够精细

    :param start_time: 开始时间
    :param stop_time: 结束时间
    :return: 时间差（string ）
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
    + 说明：
        (废弃?)
        测试例开始/结束计时

    :param test_case_name: 测试用例名称
    :param switch: 目前接受参数为：‘start’, ‘end’ 不区分大小写
    :param args: msg
    :param args: other args
    :return: 格式化输出
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
    + 说明：
        测试例开始/结束计时

        >>> with print_timer_context('hello, world') as doctest:
        >>>    print(doctest)

    :param test_case_name: 测试用例名称
    :param args: msg
    :param kwargs: other args
    :return: 格式化输出

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
    + 说明：
        检查测试例step对错，打印并记录

    :param sheet_name: 测试用例sheet名称
    :param result: 测试结果列表
    """
    if 0 in result:  # 如果result列表中存在0表示测试用例失败
        log(f'{sheet_name} is FAILED!', result, level='error')
        r = False
    else:
        log(sheet_name + ' ' + 'is PASSED', result, level='info')
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
    + 说明：
        判断字符串中存在汉字的数量

    :param msg: 需要被统计字符串
    :return: 汉字的数量
    """
    return [is_chinese(_s) for _s in msg].count(True)


def print_format(*msg):
    """
    + 说明：
        用于测试用例格式化打印输出。

    :param msg: 输入需要输出的信息
    :return: 格式化输出

    >>> print(print_format('hello', 'world'))
    ####################################################################################################
    # hello                                                                                            #
    # world                                                                                            #
    ####################################################################################################
    >>> print(print_format('hello', '你好'))
    ####################################################################################################
    # hello                                                                                            #
    # 你好                                                                                             #
    ####################################################################################################

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
    + 说明：
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
    说明+：
        如果use_cwd=True，会从当前路径依次从里到外递归查找filename，如果找到返回该文件存在路径，差找不到返回。

        如果use_cwd=False， 会从当前调用本函数的python模块所在路径开始从里到外递归查询文件，直到找到或者为。

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
    + 说明：
        允许parameters被传递到docstring中的装饰器

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
    + 说明：
        对传入的list进行递归清除每个元素中的空格


    :param nested_list: 需要进行处理的list，如果不为list触发ValueError异常
    :param evaluate: 是否需要对其中元素进行eval运算
    :return: 直接对传入的nested_list进行修改，无返回值

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
    + 说明：
        输入string，将输入的string转换成对应的原始python类型，转换失败原样输出
        如果输入不是string类型抛出异常

    >>> str_eval('123')
    123
    >>> str_eval('[1,2,3,]')
    [1, 2, 3]
    >>> str_eval('{1,2,3}')
    {1, 2, 3}
    >>> str_eval({'a':1,'b':{'c':2}})
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "<input>", line 6, in str_eval
    AttributeError: 'dict' object has no attribute 'strip'
    >>> str_eval("{'a':1,'b':{'c':2}}")
    {'a': 1, 'b': {'c': 2}}
    >>> str_eval('test')
    'test'
    >>> str_eval('!@#$%')
    '!@#$%'
    >>> str_eval('  [1, 2,3,4] ')
    [1, 2, 3, 4]
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


# noinspection PyArgumentList
class DcnDict(dict):
    """
    + 说明：
        invoke from https://github.com/mewwts/addict/blob/master/addict/addict.py
        增强版支持递归创建和引用

        >>> test = {
        ...                'query': {
        ...                    'filtered': {
        ...                        'query': {
        ...                            'match': {'description': 'addictive'}
        ...                        },
        ...                        'filter': {
        ...                            'term': {'created_by': 'Mats'}
        ...                        }
        ...                    }
        ...                }
        ...            }
        >>> body = DcnDict()
        >>> body.query.filtered.query.match.description = 'addictive'
        >>> body.query.filtered.filter.term.created_by = 'Mats'

        >>> o = DcnDict(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """

    # noinspection PyMethodParameters,PyMissingConstructor
    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, '__parent', kwargs.pop('__parent', None))
        object.__setattr__(__self, '__key', kwargs.pop('__key', None))
        for _arg in args:
            if not _arg:
                continue
            elif isinstance(_arg, dict):
                for key, val in _arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(_arg, tuple) and (not isinstance(_arg[0], tuple)):
                __self[_arg[0]] = __self._hook(_arg[1])
            else:
                for key, val in iter(_arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        super(DcnDict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __missing__(self, name):
        return self.__class__(__parent=self, __key=name)

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    def update(self, *args, **kwargs):
        other = {}
        if args:
            if len(args) > 1:
                raise TypeError()
            other.update(args[0])
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or
                    (not isinstance(self[k], dict)) or
                    (not isinstance(v, dict))):
                self[k] = v
            else:
                self[k].update(v)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def __repr__(self):
        return '<DcnDict ' + dict.__repr__(self) + '>'
