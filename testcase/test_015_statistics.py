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
#       - 2018/8/24 18:23  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestStatistics(unittest.TestCase):
    @run()
    def test_device_for_pie(self):
        pass

    @run()
    def test_ap_by_org(self):
        pass

    @run()
    def test_user_by_org(self):
        pass

    @run()
    def test_stat_for_map(self):
        pass

    @run()
    def test_user_tendency(self):
        pass

    @run()
    def test_channel_tendency(self):
        pass

    @run()
    def test_sta_info(self):
        pass
