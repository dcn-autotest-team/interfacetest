#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_init_root_org.py
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

from api.systeminit import SystemInit
from api.user import User
from library.unittest import data


class TestInitRootOrg(unittest.TestCase):
    """
    初始化根组织机构
    """
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

    @data(123, 'test', '')
    def test_step_one(self, name):
        """初始化根节点接口成功"""
        json_data = {
            'rootOrgName':name
        }
        self.assertTrue(self.system_init.check_system_initial_state(output=True).check)
        self.assertTrue(self.system_init.init_root_org(json_data=json_data, output=True).check)

if __name__ == '__main__':
    unittest.main()
