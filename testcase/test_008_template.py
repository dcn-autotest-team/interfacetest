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


class TestAuthManagement(unittest.TestCase):
    @run()
    def test_template(self):
        pass

    @run()
    def test_get_templates(self):
        pass

    @run()
    def test_get_template(self):
        pass

    @run()
    def test_add_thumb(self):
        pass

    @run()
    def test_add_template(self):
        pass

    @run()
    def test_update_template(self):
        pass

    @run()
    def test_delete_template(self):
        pass

    @run()
    def test_batch_delete_portal_template(self):
        pass

    @run()
    def test_show_pic(self):
        pass
