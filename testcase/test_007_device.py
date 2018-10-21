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
#       - 2018/8/24 18:19  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestDevManagement(unittest.TestCase):
    @run()
    def test_create_ap(self):
        pass

    @run()
    def test_ap_info(self):
        pass

    @run()
    def test_query_ap(self):
        pass

    @run()
    def test_count(self):
        pass

    @run()
    def test_online_ap(self):
        pass

    @run()
    def test_online_user(self):
        pass

    @run()
    def test_delete_ap(self):
        pass

    @run()
    def test_batch_delete_ap(self):
        pass

    @run()
    def test_modify_ap(self):
        pass

    @run()
    def test_batch_modify_ap(self):
        pass

    @run()
    def test_batch_import(self):
        pass

    @run()
    def test_reboot(self):
        pass

    @run()
    def test_dev_export(self):
        pass

    @run()
    def test_ac_info(self):
        pass

    @run()
    def test_get_ac_info(self):
        pass

    @run()
    def test_create_ac(self):
        pass

    @run()
    def test_update_ac(self):
        pass

    @run()
    def test_delete_ac(self):
        pass

    @run()
    def test_batch_delete_ac(self):
        pass
