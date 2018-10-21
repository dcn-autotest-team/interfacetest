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
#       - 2018/7/30 16:41  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from testcase.helper import run
from library.unittest import tag, Tag


class TestOrg(unittest.TestCase):

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
    def test_org_tree(self):
        pass

    @run()
    def test_update_parent(self):
        pass

    @run()
    def test_org_import(self):
        pass

    @run()
    def test_org_export(self):
        pass

    @run()
    def test_org_page(self):
        pass

    @run()
    def test_query_org(self):
        pass

    @run()
    def test_create_org(self):
        pass

    @run()
    def test_org_update(self):
        pass

    @run()
    def test_org_info(self):
        pass

    @run()
    def test_org_name(self):
        pass

    @run()
    def test_delete_org(self):
        pass

    @run()
    def test_batch_delete_org(self):
        pass

    # 需要填充用户组相关接口的其他测试点
    if __name__ == '__main__':
        unittest.main()
