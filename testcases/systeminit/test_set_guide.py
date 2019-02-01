#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_set_guide.py
#
# Author    :yanwh(yanwh@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd
#
#
# *********************************************************************
# Change log:
#       - 2019/1/30 15:34  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
import unittest

from api.systeminit import SystemInit
from api.user import User
from library import private_status_codes as codes


class TestChangeUserInfo(unittest.TestCase):
    user = User()
    system_init = SystemInit()
    @classmethod
    def setUpClass(cls):
        """超级管理员登陆"""
        cls.assertTrue(cls(), cls.user.login_super_admin().check)

    @classmethod
    def tearDownClass(cls):
        """"""
        pass

    def setUp(self):
        """"""
        pass

    def tearDown(self):
        """"""
        pass

    def test_step_one(self):
        """"""
        self.assertTrue(self.system_init.check_system_initial_state(output=True).check)

if __name__ == '__main__':
    unittest.main()