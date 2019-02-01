#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_change_password.py
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
#       - 2019/1/30 9:06  add by yanwh
#
# *********************************************************************
"""
module doc string
测试密码修改功能
"""
import unittest

from api.service import Service
from api.user import User
from config import service as service_settings
from library import private_status_codes as codes
from library.unittest import data, skip


class TestChangeUserInfo(unittest.TestCase):
    user = User()
    service = Service()
    service_model = service_settings['change_user_info']

    @classmethod
    def setUpClass(cls):
        """创建普通用户和管理员用户"""
        cls.assertTrue(cls(), cls.user.login_super_admin())

    @classmethod
    def tearDownClass(cls):
        """删除创建用户，执行清理操作"""
        pass

    def setUp(self):
        """每个测试用例开始执行拷贝一份之前构造好的post data"""
        pass

    def tearDown(self):
        """每个测试用例结束之后恢复post data"""
        pass

    @skip('接口变换，此用例暂时不执行')
    @data({'newPw': '12345678', 'oldPw': '12345678'}, unpack=False)
    def test_step_one(self, json_data):
        """用户修改密码"""
        # 用户登陆退出
        response = self.service.change_password(output=True, json_data=json_data)
        self.assertEqual(response.status, codes.SUCCESSFUL_OPERATION)

if __name__ == '__main__':
    unittest.main()
