#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_get_out_public_group_user.py
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
#       - 2019/1/23 14:56  add by yanwh
#
# *********************************************************************
"""
测试牵出公共用户组用户
"""

import logging
import unittest

from api.user import *
from config import private_status_codes
from library.log import log_instance
from library.unittest import data

log_instance.setup(console_level=logging.INFO)


class TestGetOutPublicGroupUser(unittest.TestCase):
    session = session
    user_list = []

    @classmethod
    def setUpClass(cls):
        """环境初始化，用管理员账号登陆系统创建2个用户"""
        user_one = {
            "name": "aaaa1",
            "account": "aaaa1",
            "password": "55555555",
            "email": "aaaa1@yellowstone.org",
            "phone": "13016413999",
            "status": 0,
            "role": 0,
            "position": "",
            "group": 2,
            "org": 1
        }

        user_two = {
            "name": "aaaa2",
            "account": "aaaa2",
            "password": "55555555",
            "email": "aaaa2@yellowstone.org",
            "phone": "13016413998",
            "status": 0,
            "role": 0,
            "position": "",
            "group": 2,
            "org": 1
        }

        self = cls()
        cls.assertTrue(self, super_admin_login(), '管理员登陆失败')
        for user in (user_one, user_two):
            _user_id = create_user(json=user)
            cls.assertGreaterEqual(self, a=_user_id, b=0, msg=f"初始化测试用例环境,创建用户{user['account']}失败")
            cls.user_list.append((_user_id, user))

    def setUp(self):
        """
        默认情况下面保证每个步骤中默认使用管理员登陆成功
        :return:
        """
        self.assertTrue(super_admin_login(), '管理员登陆失败')

    def tearDown(self):
        """
        pass
        :return:
        """
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        """
        进行会话清理,恢复创建的用户。
        :return:
        """
        for _user_id, _ in cls.user_list:
            delete_user(_user_id)
        cls.session.close()

    def test_step_one(self):
        """用户单位调出-操作成功"""
        response = self.session.put('user/unitOut', json={"ids": [self.user_list[0][0], ]})
        response_json_data = response.json()
        # noinspection PyUnresolvedReferences
        self.assertEqual(response_json_data['status'], private_status_codes.SUCCESSFUL_OPERATION,
                         private_status_codes.codes.get(response_json_data['status']))

    @data('test123', 'test456', 'test789')
    def test_step_two(self, user_ids):
        """用户单位调出-非法参数"""
        response = self.session.put('user/unitOut', json={"ids": [user_ids]})
        response_json_data = response.json()
        # noinspection PyUnresolvedReferences
        # 跟需求文档不符
        self.assertEqual(response_json_data['status'], private_status_codes.SERVER_INTERNAL_ERROR,
                         private_status_codes.codes.get(response_json_data['status']))

    def test_step_three(self):
        """用户单位调出-无权限操作"""
        user_login({
            'account': self.user_list[1][1].get('account'),
            'password': self.user_list[1][1].get('password')
        })
        response = self.session.put('user/unitOut', json={"ids": [self.user_list[0][0]]})
        response_json_data = response.json()

        # noinspection PyUnresolvedReferences
        self.assertEqual(response_json_data['status'], private_status_codes.UNAUTHORIZED_OPERATION,
                         private_status_codes.codes.get(response_json_data['status']))

    def test_step_four(self):
        """用户单位调出-用户不存在"""
        if get_nonexistent_user_id():
            nonexistent_user_id = user_id
        response = self.session.put('user/unitOut', json={"ids": [nonexistent_user_id]})
        response_json_data = response.json()
        # noinspection PyUnresolvedReferences
        self.assertEqual(response_json_data['status'], private_status_codes.USER_NOT_EXISTS,
                         private_status_codes.codes.get(response_json_data['status']))


if __name__ == '__main__':
    unittest.main()