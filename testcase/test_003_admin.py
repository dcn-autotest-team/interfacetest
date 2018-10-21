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
#       - 2018/8/24 17:55  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestAdmin(unittest.TestCase):

    @classmethod
    @run()
    def setUpClass(cls):
        print('Initialization is completed')

    @classmethod
    @run()
    def tearDownClass(cls):
        print('Uninitialized is completed')

    # def setUp(self):
    #     print('test start')
    #
    # def tearDown(self):
    #     print('test stop')
    @run()
    def test_admin_info(self):
        pass

    @run()
    def test_admin_model(self):
        pass

    @run()
    def test_sys_admin_model(self):
        pass

    @run()
    def test_admin_id(self):
        pass

    @run()
    def test_admin_assign(self):
        pass

    @run()
    def test_admins_assign(self):
        pass

    @run()
    def test_del_admins(self):
        pass

    @run()
    def test_search_by_phone(self):
        pass
