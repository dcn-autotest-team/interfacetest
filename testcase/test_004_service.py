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


class TestService(unittest.TestCase):
    @run()
    def test_change_user_info(self):
        pass

    @run()
    def test_login_status(self):
        pass

    @run()
    def test_change_password(self):
        pass
