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
#       - 2018/8/24 18:22  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestLog(unittest.TestCase):
    @run()
    def test_get_syslog(self):
        pass

    @run()
    def test_get_user_log(self):
        pass

    @run()
    def test_log_export(self):
        pass

    @run()
    def test_batch_delete_log(self):
        pass

    @run()
    def test_delete_log(self):
        pass

    @run()
    def test_get_dev_log(self):
        pass

    @run()
    def test_dev_log_export(self):
        pass

    @run()
    def test_batch_delete_dev_log(self):
        pass

    @run()
    def test_delete_dev_log(self):
        pass
