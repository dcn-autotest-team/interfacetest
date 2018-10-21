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


class TestDesktop(unittest.TestCase):
    @run()
    def test_upload_desktop_img(self):
        pass

    @run()
    def test_get_desktop_img(self):
        pass

    @run()
    def test_delete_desktop_img(self):
        pass

    @run()
    def test_get_interfaces_with_current_user(self):
        pass

    @run()
    def test_get_apps(self):
        pass

    @run()
    def test_add_app(self):
        pass

    @run()
    def test_get_to_desktop(self):
        pass
