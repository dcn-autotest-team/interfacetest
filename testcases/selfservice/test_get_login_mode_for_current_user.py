#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_get_login_mode_for_current_user.py
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
#       - 2019/1/27 9:24  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
import unittest

from api.service import Service
from api.user import User
from config import service as service_settings
from library import private_status_codes as codes


class TestChangeUserInfo(unittest.TestCase):
    user = User()
    service = Service()
    service_model = service_settings['change_user_info']

    @classmethod
    def setUpClass(cls):
        """创建普通用户和管理员用户"""
        pass

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

    def test_step_one(self):
        """用户未登陆情况下查询用户状态"""
        # 用户登陆退出
        self.user.logout_user()
        response = self.service.get_login_mode_for_current_user(output=True).to_json()
        self.assertEqual(response.status, codes.SESSION_USER_NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
