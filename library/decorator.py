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
from threading import Lock


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
