#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# __init__.py - 
#
# Author    :wangxinae(wangxinae@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd 
#
#
# *********************************************************************
# Change log:
#       - 2018/7/30 16:16  add by wangxinae
#
# *********************************************************************
from pathlib import Path

from library.unittest.runner import TestRunner
from projectsettings import settings, setup


if __name__ == '__main__':
    setup()
    # discovery参数支持如下特性
    # 注意 通过.的方式导入测试用例的时候目前存在缺陷，需要将settings.ini中SORT_CASE=False
    # 支持绝对引入
    # 'interfacetest.testcase.test_001_user' -->模块路径
    # 'interfacetest.testcase.test_001_user.TestUser' -->测试类
    # 'interfacetest.testcase.test_001_user.TestUser.test_user_account_export' --> 测试类里面方法
    # =====================================================
    # 支持相对引入top_level_dir= settings.DCN_TESTCASE_PATH（也就是E:\interfacetest\testcase）
    # '.test_001_user'-->模块路径
    # '.test_001_user.TestUser' -->测试类
    # '.testcase.test_001_user.TestUser.test_user_account_export' --> 测试类里面方法
    # ====================================================
    # 支持list or tuple
    # ['interfacetest.testcase.test_001_user' -->模块路径, 'interfacetest.testcase.test_002_org']
    # ['interfacetest.testcase.test_001_user' -->模块路径, '.test_002_org.TestOrg' -->测试类]
    # =====================================================
    # 支持测试路径例如 E:\interfacetest\testcase
    # 支持路径列表 [E:\interfacetest\testcase1,E:\interfacetest\testcase2]
    # 支持模块不过要在setup()之后导入(目前存在的缺陷，因为测试用例依赖于settings执行，如果在setup之前settings没有被初始化)
    # from interfacetest.testcase.test_001_user import TestUser -->测试类
    # from interfacetest.testcase import test_001_user --> 测试模块
    # =======================================================
    # 支持配置文件 todo（json/yaml/ini/dict没有应用场景）
    # =======================================================
    # 支持 Unix shell style路径查找,用法如下:
    #
    #    Patterns are Unix shell style:
    #
    #    *       matches everything
    #    ?       matches any single character
    #    [seq]   matches any character in seq
    #    [!seq]  matches any char not in seq
    # C\test*.py==>查找C:\下面以test开始和以.py结尾测试用例
    # =========================================================
    # 支持a callable object which returns a TestCase or TestSuite instance todo
    # =========================================================
    # 支持(path-like objects)对象传入，例如Path('E://') or 实现了__fspath__的类对象实例
    # 支持原有的settings.ini中的Unittest中的配置
    # 同时配置文件中的标签功能依旧生效，也就是如果配置中打了{Tag.SP}之后如果测试用例没有打上对应标记，后续导入方法无效
    # =========================================================
    runner = TestRunner()
    runner.run_test(settings.report_file, report_title='接口自动化测试报告',
                    top_level_dir=Path(settings.DCN_TESTCASE_PATH),
                    discovery=r'E:\wirelessinterfacetest\interfacetest\testcase\test*.py')

