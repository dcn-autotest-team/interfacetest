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
#       - 2018/7/27 18:13  add by wangxinae
#
# *********************************************************************
from library.basesheetdata import OperationExcel
from library.sessionmethod import SessionMethod
from library.utils import print_timer_context
from library.log import log

from library.conf import settings


class Api:
    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name

    def api(self):
        """
        函数作用：输入需要测试的excel中sheet名称，获取sheet表中每行的测试用例编号，测试用例名称，预制条件，url,
        data，request方法和响应码，测试每张sheet表中不同的测试例。
        :return: 返回每张sheet中各个测试例结果的列表
        """
        excel = OperationExcel(self.file_name, self.sheet_name)
        seq = excel.get_seq
        name = excel.get_name
        url = excel.get_url
        data = excel.get_date
        method = excel.get_method
        code = excel.get_code
        row = excel.get_rows
        error_code = excel.get_error_code
        # 通过http调用接口后返回状态码有两种形态，分别保存在code[]和error_code[]两个列表中
        res = []
        for i in range(0, row - 1):
            full_url = settings.base_url + str(url[i])
            with print_timer_context(f'{seq[i]} {name[i]}'):
                api = SessionMethod(full_url, data[i], seq[i])
                stat = {'status': None}
                request = {"post": api.post, "get": api.get, "put": api.put, "delete": api.delete, "head": api.head,
                           "patch": api.patch, "option": api.option, "postuser": api.post_user,
                           "getuser": api.get_user,
                           "putuser": api.put_user, "deleteuser": api.delete_user, "postadmin": api.post_admin,
                           "getadmin": api.get_admin,
                           "putadmin": api.put_admin, "deleteadmin": api.delete_admin,
                           "postnologin": api.post_no_login, "getnologin": api.get_no_login,
                           "putnologin": api.put_no_login, "deletenologin": api.delete_no_login}
                for key in request:
                    if key == method[i]:
                        stat = request[key]()
                        break
                else:
                    log('interface test method is error', level='info')

                # 下面代码作用为根据返回结果判断测试是否通过
                if code[i] != "" and stat["status"] == code[i]:
                    # 使用状态码code[]来判断的情况
                    log(f'[Match Code: {code[i]} is OK!] TestCase {seq[i]} is Passed', level='info')
                    res.append(1)
                elif code[i] == "" and error_code[i] != "" and stat["status"] != 0:
                    # 使用状态码error_code[]来判断的情况,有一种特殊情况，预期不能创建成功的接口，在测试中创建成功会返回代码0，例如：
                    # {'status': 0, 'addErrors': None, 'updateErrors': None, 'delErrors': None}
                    for key in stat:
                        if (key == "errors" or key == "addErrors" or key == "delErrors" or key == "updateErrors") \
                                and isinstance(stat[key], list):
                            # 用于user->“组织机构用户组批量操作”or“批量删除用户组”测试判断
                            # {'status': 7, 'errors': [{'id': 14, 'status': 1}, {'id': 7, 'status': 163}]}
                            for d in range(len(stat[key])):
                                # 遍历关键字为"errors"or"addErrors"or"delErrors"or"updateErrors"的字典所对应值的列表，这里列表所对应
                                # 的元素个数是变化的
                                if stat[key][d].get("status") == error_code[i] or stat[key][d].get("code") == error_code[i]:
                                    # 列表中每一个元素都是字典类型，取字典中关键字"status"对应的错误码，用来做判断
                                    log(f'[Match ErrorCode: {error_code[i]} is OK!] TestCase {seq[i]} is Passed',
                                        level='info')
                                    res.append(1)
                                    # 如果错误码和预期一致，目前遇到的返回码只涉及到关键字"errors"or"addErrors"or"delErrors"
                                    # or"updateErrors"中的一种，所以一旦找到就退出循环
                                    break
                            else:
                                log(f'[Not Match ErrorCode: {error_code[i]}] TestCase {seq[i]} is Failed',
                                    level='error')
                                res.append(0)
                                # 整个错误码对应列表中的字典元素都和预期错误码不一致，记为测试fail
                        elif (key == 'result') and isinstance(stat[key], dict):
                            # 用于user->"用户账号批量导入"测试判断
                            # {"status":4,"result":{"count":4,"errors":[{"index":5,"code":251},{"index":6,"code":252},
                            # {"index":7,"code":252},{"index":8,"code":252}]}}
                            if stat[key]['count'] == error_code[i] or \
                                    ('errors' in stat[key] and error_code[i] == 'errors'):
                                # 判断count或者errors是否与错误检查点一致
                                log(f'[Match ErrorCode: {error_code[i]} is OK!] TestCase {seq[i]} is Passed',
                                    level='info')
                                res.append(1)
                            else:
                                for b in range(len(stat[key]['errors'])):
                                    # 遍历关键字为"errors"的字典所对应值的列表，这里列表所对应的元素个数是变化的
                                    if stat[key]['errors'][b].get("index") == error_code[i] \
                                            or stat[key]['errors'][b].get("code") == error_code[i]:
                                        # 列表中每一个元素都是字典类型，取字典中关键字"index"或者“code”对应的错误码，用来做判断
                                        log(f'[Match ErrorCode: {error_code[i]} is OK!] TestCase {seq[i]} is Passed',
                                            level='info')
                                        res.append(1)
                                        # 如果错误码和预期一致，目前遇到的返回码只涉及到关键字"code"or"index"中的一种，
                                        # 所以一旦找到就退出循环
                                        break
                                else:
                                    log(f'[Not Match ErrorCode: {error_code[i]}] TestCase {seq[i]} is Failed',
                                        level='error')
                                    res.append(0)
                                    # 整个错误码对应列表中的字典元素都和预期错误码不一致，记为测试fail
                        elif (key == 'result') and not isinstance(stat[key], dict):
                            # org->组织机构导入-IP格式不正确{"status":3,"result":null}
                            log(f'[Not Match ErrorCode: {error_code[i]}] TestCase {seq[i]} is Failed',
                                level='error')
                            res.append(0)

                elif code[i] == "" and stat["status"] == 0:
                    log(f'[The Reason for TestCase {seq[i]} Failure is function problem', level='error')
                    res.append(0)
                else:
                    log(f'[Not Match Code: {code[i]}] TestCase {seq[i]} is Failed', level='error')
                    res.append(0)
        return res


