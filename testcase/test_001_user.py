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
#       - 2018/7/30 14:45  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run
from library.unittest import tag, Tag


class TestUser(unittest.TestCase):

    @classmethod
    @run()
    def setUpClass(cls):
        print('Initialization is completed')

    @classmethod
    @run()
    def tearDownClass(cls):
        print('Uninitialized is completed')

    @tag(Tag.SP)
    @run()
    def test_user_unit_out(self):
        pass

    @run()
    def test_public_user_out(self):
        pass

    @run()
    def test_user_account_import(self):
        pass

    @run()
    def test_user_account_export(self):
        pass

    @run()
    def test_user_login(self):
        pass

    @run()
    def test_user_login_out(self):
        pass

    @run()
    def test_create_user(self):
        pass

    @run()
    def test_update_user(self):
        pass

    @run()
    def test_delete_user(self):
        pass

    @run()
    def test_query_user(self):
        pass

    @run()
    def test_user_info(self):
        pass

    @run()
    def test_batch_update_user(self):
        pass

    @run()
    def test_batch_delete_user(self):
        pass

    @run()
    def test_login_user_interface(self):
        pass

    @run()
    def test_modify_password(self):
        pass

    @run()
    def test_group_info(self):
        pass

    @run()
    def test_create_org_group(self):
        pass

    @run()
    def test_update_group(self):
        pass

    @run()
    def test_delete_group(self):
        pass

    @run()
    def test_batch_delete_user_group(self):
        pass

    @run()
    def test_batch_org_user(self):
        pass

    @run()
    def test_user_group_info(self):
        pass

    # 需要填充用户组相关接口的其他测试点

    if __name__ == '__main__':
        unittest.main()
