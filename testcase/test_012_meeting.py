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
#       - 2018/8/24 18:21  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestMeeting(unittest.TestCase):
    @run()
    def test_create_meeting(self):
        pass

    @run()
    def test_get_meetings(self):
        pass

    @run()
    def test_get_meeting(self):
        pass

    @run()
    def test_modify_meeting(self):
        pass

    @run()
    def test_delete_meeting(self):
        pass

    @run()
    def test_batch_delete(self):
        pass

    @run()
    def test_get_ssid(self):
        pass
