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
#       - 2018/8/24 18:20  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestUserAuth(unittest.TestCase):
    @run()
    def test_sms(self):
        pass

    @run()
    def test_auth(self):
        pass

    @run()
    def test_un_auth(self):
        pass

    @run()
    def test_visitor_auth(self):
        pass

    @run()
    def test_qr_code(self):
        pass

    @run()
    def test_qr_code_auth(self):
        pass

    @run()
    def test_get_page_at_groups_within_permissions(self):
        pass

    @run()
    def test_query_network_group_mapping(self):
        pass
