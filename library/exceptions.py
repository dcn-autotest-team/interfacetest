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
    单例模式初始化参数不得修改
    """

    def __init__(self, msg=''):
        msg = f'[单例模式错误]: {msg}.'
        super(self.__class__, self).__init__(msg)


class ConstError(DcnError):
    """
    常量异常类
    """

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
