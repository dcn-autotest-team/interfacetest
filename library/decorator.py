#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# decorator.py - 通用装饰器
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
#       - 2018/9/20 16:03  add by yanwh
#
# *********************************************************************
"""
    + 模块说明：
        装饰器相关的函数和类
"""
import time
from typing import List, Tuple, Union, Callable
from functools import wraps
from threading import Lock


def retry(timeout: Union[int, float] = 10, interval: Union[int, float] = 0.5, exceptions: Union[List, Tuple] = (),
          verify: Callable = None, silent: bool = False):
    """
    + 说明：
        装饰器用于每隔固定的interval检测被调用的函数是否在timeout内返回预期的结果，
        成功返回被装饰的函数调用结果，超时抛出TimeOutError异常。

    :param interval: 尝试时间间隔(默认0.5s)
    :param timeout: 尝试超时总时长(默认10s)
    :param exceptions: 被装饰函数调用期间产生的异常在exceptions中，触发重试。
                       默认为空,则不捕获异常。
    :param verify: 验证被装饰函数调用之后返回值是否符合预期，
                   当verify(ret)返回True时，直接返回，否则继续retry。
                   默认值为None，不验证直接返回。
    :param silent: 如果为True，则不抛出TimeOutError异常。
    :return: 装饰器函数，用于调用被装饰的函数执行。
             成功返回调用func的结果，失败抛出TimeOutError异常。

    """
    timeout = float(timeout)
    interval = float(interval)

    def decorate(func: callable):
        """
        :param func: 被装饰的需要进行反复尝试的函数
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            :param args: 被装饰的需要进行反复尝试的参数
            :param kwargs: 被装饰的需要进行反复尝试的参数
            :return: function
            """
            start = time.time()
            try_count = 0
            ret = None
            while True:
                try:
                    try_count += 1
                    ret = func(*args, **kwargs)
                    if verify is None or verify(ret):
                        return ret
                except exceptions:
                    pass
                waited = time.time() - start
                if waited < timeout:
                    time.sleep(min(interval, timeout - waited))  # 此处不能单纯的使用self.interval，
                    # 防止当interval>waited的时候如果还是取interval，导致总共的timeout时间大于设定的timeout，或者另外
                    # 一种情况就是interval默认取值就大于timeout
                elif try_count == 1:  # 防止当timeout设置的过于小以至于小到了小于waited的时间 导致ret没有经过func(*args or **args)
                    continue
                else:
                    if silent:
                        return ret
                    else:
                        err_msg = f'在{timeout}秒里尝试了{try_count}次'
                        raise TimeoutError(err_msg)

        return wrapper

    return decorate


def check(expect: object, timeout: [int, float] = 10, interval: [int, float] = 0.5):
    """
    + 说明：
        装饰器用于每隔固定的interval检测被调用的函数是否在timeout内返回符合expect设定的期望值，成功返回True，超时False

    :param interval: 尝试时间间隔(默认0.5s)
    :param timeout: 尝试超时总时长(默认10s)
    :param expect: 设定的期望值
    :return: 被装饰的函数调用结果符合except，返回True，否则False

    """
    timeout = float(timeout)
    interval = float(interval)

    def decorate(func: callable):
        """
        :param func: 被装饰的需要进行反复尝试的函数
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            :param args: 被装饰的需要进行反复尝试的参数
            :param kwargs: 被装饰的需要进行反复尝试的参数
            :return: function
            """

            start = time.time()
            while 1:
                if expect == func(*args, **kwargs):
                    return True
                waited = time.time() - start
                if waited < timeout:
                    time.sleep(min(interval, timeout - waited))
                else:
                    return False

        return wrapper

    return decorate


class Singleton:
    """
    作用于用户类的装饰器，使得被装饰的类生产的对象均为同一对象
    注意初始化单例模式的参数应该固定,否则抛出SingletonError

    >>> ts=TestSingleton(1)
    >>> tss=TestSingleton(1)
    >>> ts==tss
    True
    >>> ts.x, ts.y
    (1, 12)
    """

    def __init__(self, cls):
        self.__instance = self._args = self._kwargs = None
        self.__cls = cls
        self._lock = Lock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            if self.__instance is None:
                self._args = args
                self._kwargs = kwargs
                self.__instance = self.__cls(*args, **kwargs)
            elif any([self._args != args, self._kwargs != kwargs]):
                from .exceptions import SingletonError
                raise SingletonError('单例模式的参数设定之后不允许修改')
            return self.__instance


class SingletonMeta(type):
    """
    单例模式元类实现方式
    注意初始化单例模式的参数应该固定唯一,否则抛出SingletonError

    >>> tsm=TestSingletonMeta(1,2)
    >>> tsm1=TestSingletonMeta(1,2)
    >>> tsm1==tsm
    True
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = cls._args = cls._kwargs = None
        cls._lock = Lock()
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls.__instance is None:
                cls._args = args
                cls._kwargs = kwargs
                cls.__instance = super().__call__(*args, **kwargs)
            elif any([cls._args != args, cls._kwargs != kwargs]):
                from .exceptions import SingletonError
                raise SingletonError('单例模式的参数设定之后不允许修改')
            return cls.__instance


# test-------------------------------------------------------------------------------------------
@Singleton
class TestSingleton:
    """
    use for doctest
    """

    def __init__(self, x, y=12):
        self.x = x
        self.y = y


class TestSingletonMeta(metaclass=SingletonMeta):
    """
    use for doctest
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


if __name__ == '__main__':
    import doctest

    doctest.testmod()
