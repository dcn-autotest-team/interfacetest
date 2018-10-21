#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# loader.py - 
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
#       - 2018/10/16 19:29  add by yanwh
#
# *********************************************************************
import re
from inspect import ismodule, isclass
from keyword import kwlist
from pathlib import Path
from unittest import TestLoader, TestSuite

import sys

import os

from library.conf import settings
from library.exceptions import InvalidArgument, InvalidPath, ParsePathError, TestCaseNotFound
from library.log import log

DOT_MODULE_MATH = re.compile('([A-Za-z_]+\w*\.)+([A-Za-z_]+\w*)$')  # 匹配 a.b.c


def valid_import_path(path):
    """
    输入路径，输出可以进行import的路径
    :param path:
    :return:
    """
    parts = Path(path).resolve().parts[1:]

    def _join(_parts):
        return '.'.join(_parts)

    while parts:
        try:
            __import__(_join(parts))
            break
        except ImportError:
            parts = parts[1:]
    return _join(parts)


class Loader(TestLoader):
    def __init__(self, top_level_dir=None):
        super(TestLoader, self).__init__()
        self.top_level_dir = top_level_dir
        self._suite = TestSuite()

    @property
    def suite(self):
        return self._suite

    def _parse_path(self, discovery):
        log(" parse path", level='info')
        discovery = Path(discovery).resolve()
        if discovery.is_dir():  # 如果传入dir要求必须是测试用例路，不能是配置文件
            self._suite.addTests(self.discover(discovery, top_level_dir=self.top_level_dir))
            log("文件夹", level='info')
        elif discovery.is_file():  # 如果传入file要求必须是配置文件
            # todo
            if '.ini' == discovery.suffix:
                log("parse ini", level='info')
            elif '.json' == discovery.suffix:
                log('parse json', level='info')
            elif '.ymal' == discovery.suffix:
                log('parse toml', level='info')
            elif '.toml' == discovery.suffix:
                log('parse toml', level='info')
            elif '.py' == discovery.suffix:
                log('parse py', level='info')
            else:
                log('error')
        else:
            raise ParsePathError(f'无法解析{discovery}路径')

    def _parse_str(self, discovery):
        if discovery in sys.modules:  # 尝试本地命名空间中是否存在该模块存在
            log(f'\n===sys.modules===\n通过sys.modules导入{discovery}')
            self._suite.addTests(self.loadTestsFromModule(sys.modules[discovery], pattern=None))
        elif DOT_MODULE_MATH.match(discovery):  # 校验字符串合法性,匹配绝对路径
            if any([not _.isidentifier() and _ not in kwlist for _ in
                    discovery.split('.')]):
                raise InvalidArgument(f'非法参数{discovery}')
            else:
                name = discovery
                try:
                    self._suite.addTests(self.loadTestsFromName(name))  # 直接进行解析
                    log(f'\n===绝对路径===\n通过loadTestsFromNames导入{discovery}')
                except (ModuleNotFoundError, Exception):  # no qa可能路径带有具体方法???
                    parts = discovery.split('.')
                    from importlib import import_module
                    while parts:
                        try:
                            mod = import_module('.'.join(parts))
                            if callable(getattr(mod, _class)):
                                self._suite.addTest(getattr(mod, _class)(_method))
                                log(f'\n===实例化对象引入===\n通过addTest导入{mod}{_class}{_method}')
                                break
                        except ImportError:
                            _class = parts[-2]
                            _method = parts[-1]
                            parts = parts[:-2]
        elif discovery.startswith('.'):  # 如果为相对引入路径，结合top_level_dir进行相对引入
            name = valid_import_path(self.top_level_dir) + discovery
            self._suite.addTests(self.loadTestsFromName(name))
            log(f'\n===相对路径===\n通过loadTestsFromName导入{name}')

        else:
            try:
                if Path(discovery).resolve().is_dir() or Path(discovery).resolve().is_file():  # 如果传入路径进行路径解析
                    self._parse_path(discovery)  # 委托给parse_path进行解析
                else:
                    raise InvalidPath(f'无效路径 {discovery}')  # 必须为有效路径
            except OSError:
                if '*' in discovery or '?' in discovery or '.' in discovery:  # 尝试解析例如E://testcase/test_*.py
                    parent = Path(discovery).parent  # 父路径
                    pattern = Path(discovery).parts[-1]  # 正则
                    if parent.is_dir():
                        glob_path_list = list(parent.glob(pattern))
                        if len(glob_path_list):
                            from pprint import pformat
                            log(f'\n===加载如下测试用例===\n{pformat(glob_path_list)}')
                            for _ in glob_path_list:
                                valid_import_path(_.parent)
                                self._suite.addTests(
                                    self.loadTestsFromName('.'.join([valid_import_path(_.parent), _.stem])))
                        else:
                            raise TestCaseNotFound('没有找到测试用例')

                    else:
                        raise InvalidPath(f'无效路径 {discovery}')  # 必须为有效路径
                else:
                    raise InvalidArgument(f'无法解析参数 {discovery}')

    def parse(self, discovery):
        if isinstance(discovery, str):
            log("===解析字符串===")
            self._parse_str(discovery)
        elif isinstance(discovery, os.PathLike):
            log("===解析PathLike路径===")
            self._parse_path(discovery)
        elif ismodule(discovery):
            log("===解析模块===")
            self._suite.addTests(self.loadTestsFromModule(discovery, pattern=None))
        elif isclass(discovery):
            log("===解析类===")
            self._suite.addTests(self.loadTestsFromTestCase(discovery))
        elif isinstance(discovery, (list, tuple)):
            log("===解析Sequence===")
            for _discovery in discovery:
                self.parse(_discovery)

    def load(self, discovery):
        if discovery:
            self.parse(discovery)
        else:  # 默认加载方式 先从全局settings中获取，失败再从当前python文件中获取
            if settings.get('testcase_ini'):  # 尝试全局扫描到的配置文件
                log("使用自动扫描到的配置文件加载测试用例", level='info')
            else:  # 尝试通过py加载
                log("使用当前环境中的py变量加载测试用例", level='info')

