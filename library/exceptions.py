#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# exceptions.py - 
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
#       - 2018/8/15 13:21  add by yanwh
#
# *********************************************************************
"""
+ 模块说明：
    自定义异常类
"""


class DcnFailure(Exception):
    pass


class ValidationFailure(DcnFailure):
    pass


class ExtractFailure(DcnFailure):
    pass


class SetupHooksFailure(DcnFailure):
    pass


class TeardownHooksFailure(DcnFailure):
    pass


class DcnError(Exception):
    pass


class FileFormatError(DcnError):
    pass


class ParamsError(DcnError):
    pass


class NotFoundError(DcnError):
    pass


class FileNotFound(FileNotFoundError, NotFoundError):
    pass


class FrameNotFound(ValueError, NotFoundError):
    pass


class PathNotFound(IOError, NotFoundError):
    pass


class TestCaseNotFound(IOError, NotFoundError):
    pass


class FunctionNotFound(NotFoundError):
    pass


class VariableNotFound(NotFoundError):
    pass


class ApiNotFound(NotFoundError):
    pass


class TestcaseNotFound(NotFoundError):
    pass


class SingletonError(DcnError, ValueError):
    """
    说明：如果一个类的元类为单例类，或者类被单例模式装饰器装饰的前提条件下，该类一旦被初始化（__init__（x,y））后
    ，后面再次实例化类__init__(a,b)的时候会触发SingletonError，除非依旧为__init__(a,b)，异常提示信息为
    [单例模式错误]: {msg}.
    """

    def __init__(self, msg=''):
        msg = f'[单例模式错误]: {msg}.'
        super(self.__class__, self).__init__(msg)


class ConstError(DcnError):
    """
    说明 如果常量变量名不为大写，或者常量名定义之后被修改的情况下会触发常ConstError，异常提示信息为
    [常量错误]: {msg}."""

    def __init__(self, msg=''):
        msg = f'[常量错误]: {msg}.'
        super(self.__class__, self).__init__(msg)


class InvalidOption(DcnFailure, KeyError):
    pass


class InvalidPath(DcnFailure):
    pass


class InvalidPathDir(InvalidPath):
    pass


class InvalidArgument(DcnFailure):
    pass


class ImproperlyConfigured(DcnFailure):
    pass


class ParsePathError(Exception):
    pass


class InvalidConfig(Exception):
    pass


class InvalidConfigOption(Exception):
    pass
