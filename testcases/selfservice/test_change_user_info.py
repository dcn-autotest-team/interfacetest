#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# test_change_user_info.py
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
#       - 2019/1/25 16:24  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
import unittest
from copy import deepcopy

from api.service import Service
from api.user import User
from api.systeminit import SystemInit
from api.utils import make_user_info
from config import service as service_settings, system_init
from library import private_status_codes as codes
from library.unittest import data


class TestChangeUserInfo(unittest.TestCase):
    user = User()
    service = Service()
    service_model = service_settings['change_user_info']

    @classmethod
    def setUpClass(cls):
        """
        step 1 管理员登陆,assert超级管理员务必登陆成功否则后续不必执行,获取接口返回的uid
        step 2 调用用户查询接口，获取该uid对应的详细账号信息
        step 3 将获取的账号信息转换成change user info接口调用的元数据
        """
        system = SystemInit()
        inited = system_init.check_system_initial_state.inited
        self = cls()
        ret = cls.user.login_super_admin()
        cls.assertTrue(self, ret.check, '超级管理员登陆失败，请检查配置')
        sys_ret = system.check_system_initial_state()
        cls.assertTrue(self, sys_ret.check)
        cls.assertEqual(self, sys_ret.response.inited, inited.initialized.value, '设备没有初始化，请初始化')
        cls.meta_user_info = make_user_info(ret.response.result)

    @classmethod
    def tearDownClass(cls):
        """删除创建用户，执行清理操作"""
        self = cls()
        ret = cls.user.login_super_admin()
        cls.assertTrue(self, ret.check, '超级管理员登陆失败，请检查配置')
        ret = cls.service.change_user_info(cls.meta_user_info)
        cls.assertTrue(self, ret.check, '恢复修改超级管理员默认信息失败，请检查接口')

    def setUp(self):
        """每个测试用例开始执行拷贝一份之前构造好的post data"""
        self.json_data = deepcopy(self.meta_user_info)

    def tearDown(self):
        """每个测试用例结束之后恢复post data"""
        self.json_data = deepcopy(self.meta_user_info)

    @data('Ywh123456', '!@#!@#!@#!@#!@#', '123', '111111111111111111111111111111',
          '12345678', '111111111111111111111111111111111111111111111111111111111'
          )
    def test_step_001(self, new_password):
        """超级管理员用户修改密码-->修改成长度超过30的密码接口返回信息依旧是密码长度应该大于等于8位"""
        self.json_data['newPw'] = new_password
        pwd_length = len(new_password)

        if 8 <= pwd_length <= 30:
            ret = self.service.change_user_info(self.json_data, output=True)
            self.assertTrue(ret.check, '超级管理员修改密码失败')
        elif 0 < pwd_length < 8:
            ret = self.service.change_user_info(self.json_data, output=True,
                                                expect=codes.PASSWORD_LENGTH_SHOULD_GREATER_THEN_EIGHT)

            self.assertTrue(ret.check)
        else:
            # 此处为后端接口的问题，接口应该新建一个状态码表示密码长度超长，不过前端页面做了限制，此处可以忽略
            ret = self.service.change_user_info(self.json_data, output=True,
                                                expect=codes.PASSWORD_LENGTH_SHOULD_GREATER_THEN_EIGHT)
            self.assertTrue(ret.check, '超级管理员修改密码失败')

    @data({'phone': '13132131231', 'code': 1232}, {'phone': '13132131232', 'code': '123123'},
          {'phone': '131321311232', 'code': ''})
    def test_step_002(self, **kwargs):
        """超级管理员用户修改手机号,验证码为空或者错误验证码"""
        for k, v in kwargs.items():
            self.json_data[k] = v
        ret = self.service.change_user_info(self.json_data, output=True, expect=codes.SMS_VERIFICATION_CODE_ERROR)
        self.assertTrue(ret.check)

    @data('10000000111111大声道大厦大厦的撒大厦大厦大厦大声道', '@@!@!@!@!@!@!@@@@@@@@@@@@@@<dasdasd asd>')
    def test_step_003(self, phone):
        """超级管理员用户修改手机号为异常值"""
        self.json_data['phone'] = phone
        ret = self.service.change_user_info(self.json_data, output=True, expect=codes.SMS_VERIFICATION_CODE_ERROR)
        self.assertTrue(ret.check)

    @data('10000000@123.com', 'adas@digital.cn', '123')
    def test_step_004(self, email):
        """超级管理员用户修改邮箱-->此处测试管理员的邮箱没有进行校验"""
        self.json_data['email'] = email
        if '@' in email:
            ret = self.service.change_user_info(self.json_data, output=True)
            self.assertTrue(ret.check)
        else:
            ret = self.service.change_user_info(self.json_data, output=True, expect=codes.SERVER_INTERNAL_ERROR)
            self.assertTrue(ret.check)

    @data({'x': 1, 'y': 2}, {'中': 'dasd', '果盘': '123123'})
    def test_step_005(self, **kwargs):
        """超级管理员用户非法参数"""
        for k, v in kwargs.items():
            self.json_data[k] = v
        ret = self.service.change_user_info(self.json_data, output=True, expect=codes.SERVER_INTERNAL_ERROR)
        self.assertTrue(ret.check)

    @data({'account': 1}, {'account': 'dasd'})
    def test_step_006(self, **kwargs):
        """超级管理员用户非法参数-->修改超级管理员用户名的时候提示系统管理员只允许修改密码，其实系统管理员可以修改很多东西的"""
        for k, v in kwargs.items():
            self.json_data[k] = v
        ret = self.service.change_user_info(self.json_data, output=True,
                                            expect=codes.SYSTEM_ADMIN_ONLY_ALLOWED_UPDATE_PASSWORD)
        self.assertTrue(ret.check)

    @data({'account': 1}, {'account': 'dasd'})
    def test_step_007(self, **kwargs):
        """超级管理员用户非法参数-->修改超级管理员用户名的时候提示系统管理员只允许修改密码，其实系统管理员可以修改很多东西的"""
        for k, v in kwargs.items():
            self.json_data[k] = v
        ret = self.service.change_user_info(self.json_data, output=True,
                                            expect=codes.SYSTEM_ADMIN_ONLY_ALLOWED_UPDATE_PASSWORD)
        self.assertTrue(ret.check)

    @data({'name': 'admin'})
    def test_step_008(self, **kwargs):
        """普通管理员不能修改名称为admin"""
        # 创建普通管理员账号
        ret = self.user.create_common_admin()
        self.assertTrue(ret.check, '创建普通管理员返回状态码跟预期不符，创建失败')
        self.assertTrue(ret.response.id is not None, '创建普通管理员id为空，创建失败')
        try:
            # 登陆普通管理员账号获取change user info的源数据
            self.assertTrue(self.user.login_common_admin().check, '登陆普通管理员账号失败')
            json_data = make_user_info(ret.response.id)
            # 修改接口名称
            for k, v in kwargs.items():
                json_data[k] = v
            new_ret = self.service.change_user_info(json_data, output=True,
                                                    expect=codes.COMMON_USER_NOT_ALLOWED_TO_USR_NAME_ADMIN)
            self.assertTrue(new_ret.check)
        finally:
            # 登陆超级管理员账号
            self.assertTrue(self.user.login_super_admin().check)
            # 删除普通管理员账号
            self.assertTrue(self.user.delete_single_user(ret.response.id).check)

    @data({'name': 'admin'})
    def test_step_009(self, **kwargs):
        """普通用户不能修改名称为admin"""
        ret = self.user.create_common_user()
        self.assertTrue(ret.check, '创建普通用户返回状态码跟预期不符，创建失败')
        self.assertTrue(ret.response.id is not None, '创建普通用户id为空，创建失败')
        try:
            # 登陆普通用户号获取change user info的源数据
            self.assertTrue(self.user.login_common_user().check, '登陆普通用户账号失败')
            json_data = make_user_info(ret.response.id)
            # 修改接口名称
            for k, v in kwargs.items():
                json_data[k] = v
            self.assertTrue(self.service.change_user_info(json_data, output=True,
                                                          expect=codes.COMMON_USER_NOT_ALLOWED_TO_USR_NAME_ADMIN).check)
        finally:
            # 登陆超级管理员账号
            self.assertTrue(self.user.login_super_admin().check)
            # 删除普通管理员账号
            self.assertTrue(self.user.delete_single_user(ret.response.id).check)


if __name__ == '__main__':
    unittest.main()
