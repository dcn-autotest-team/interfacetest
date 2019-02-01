#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_check_system_initial_state.py
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
#       - 2019/1/30 15:33  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
import unittest
import warnings

from api.service import Service
from api.systeminit import SystemInit
from api.user import User
from api.device.device import init_device
from config import system_init

# from library import private_status_codes as codes

interface_status_codes = system_init.check_system_initial_state
inited = interface_status_codes.inited


class TestCheckSystemInitialState(unittest.TestCase):
    user = User()
    service = Service()
    system_init = SystemInit()

    @classmethod
    def setUpClass(cls):
        """超级管理员登陆"""
        cls.assertTrue(cls(), cls.user.login_super_admin().check)
        # cls.service.change_password()

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
        """设备恢复出厂设置,判断设备的初始化状态为未初始化"""
        if init_device():
            ret = self.system_init.check_system_initial_state(output=True)
            self.assertTrue(ret.check)
            self.assertEqual(ret.response.inited, inited.uninitialized.value)
        else:
            self.fail('设备初始化失败')

    def test_step_two(self):
        """初始化系统,判断设备的初始化状态为初始化"""
        # 初始化系统
        if init_device():
            self.assertTrue(self.user.login_super_admin().check)
            ret = self.system_init.check_system_initial_state(output=True)
            self.assertTrue(ret.check)
            self.assertEqual(ret.response.inited, inited.uninitialized.value)
        else:
            self.fail('设备初始化失败')


if __name__ == '__main__':
    unittest.main()
