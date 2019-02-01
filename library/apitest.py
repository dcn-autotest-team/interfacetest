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
from library.basesheetdata import OperateExcel
from library.conf import settings
from library.log import log
from library.sessionmethod import SessionMethod
from library.utils import print_timer_context


class Api(OperateExcel):
    """
    API Operate
    """
    def __init__(self, file_name, sheet_name):
        super(Api, self).__init__(file_name, sheet_name)
        self.file_name = file_name
        self.sheet_name = sheet_name

    def api(self):
        """
        + 说明：
        输入需要测试的excel名称和excel中sheet名称，获取sheet表中每行的测试用例编号，测试用例名称，预制条件，url,
        data，request方法，响应码和错误检测码，测试每张sheet表中不同的测试例。


        + 测试结果判断：
              根据获取的响应码code[i]或者错误检测码error_code[i]来判断测试例的测试结果是否pass。

           1.当获取的code[i]不为空且获取返回结果的"status"和code[i]相等，这个时候是通过code[i]即响应码来判断测试结果的。

           2.当获取的code[i]为空且error_code[i]不为空且获取返回结果的”status“不为0，这个时候是通过error_code[i]即错误响应码来判断
           测试结果的，这时根据返回结果又分为三种情况：
             情况1：
                  返回的字典结果中字典的key等于"errors" or "addErrors" or "delErrors" or "updateErrors"且这些key对应的值为一个
               列表，如{'status': 7, 'errors': [{'id': 14, 'status': 1}, {'id': 7, 'status': 163}]}，取key对应列表中的"status"
               或者"code"和error_code[i]做对比得出测试结果是否pass;
             情况2：
                  返回字典的key等于“result”且这个key对应的结果是一个字典，如{"status":4,"result":{"count":4,"errors":
               [{"index":5,"code":251},{"index":6,"code":252},{"index":7,"code":252},{"index":8,"code":252}]}}，
               这时是通过key“count"或者key“result”对应字典的key“errors”对应的值key"index"或者“code”和error_code[i]做对比得出测试结果是否pass；
             情况3：
                  返回字典的key等于“result”且这个key对应的结果不是一个字典，这是一个容错判断，直接判断测试结果为fail;

           3.当获取的code[i]为空且获取返回结果的"status"等于0，这是个容错判断，直接判断由于功能问题导致的测试结果为fail;

           4.除上述外的其他情况，判断测试结果为fail。

        :return: 返回每张sheet中各个测试例结果的列表

        """
        # noinspection PyTypeChecker
        arguments = zip(self.seqs, self.names, self.urls, self.data, self.methods, self.codes, self.error_codes)
        res = []
        for seq, name, url, data, method, code, error_code in arguments:
            full_url = settings.base_url + url
            with print_timer_context(f'{seq} {name}'):
                api = SessionMethod(full_url, data, seq)
                stat = {'status': None}
                request = {
                    "post": api.post, "get": api.get, "put": api.put, "delete": api.delete, "head": api.head,
                    "patch": api.patch, "option": api.option, "postuser": api.post_user,
                    "getuser": api.get_user,
                    "putuser": api.put_user, "deleteuser": api.delete_user, "postadmin": api.post_admin,
                    "getadmin": api.get_admin,
                    "putadmin": api.put_admin, "deleteadmin": api.delete_admin,
                    "postnologin": api.post_no_login, "getnologin": api.get_no_login,
                    "putnologin": api.put_no_login, "deletenologin": api.delete_no_login
                }
                if method not in request:
                    log('interface test method is error', level='info')
                else:
                    stat = request[method]()
                # 下面代码作用为根据返回结果判断测试是否通过
                if code != "" and stat["status"] == code:
                    # 使用状态码code[]来判断的情况
                    log(
                        f'\n[结果]:\n'
                        f'> [Except Code: {int(code)} ] | [Actual Code: {stat["status"]}] TestCase {name}({seq}) is '
                        f'Passed',
                        level='info')
                    # log(f'[Match Code: {code} is OK!] TestCase {name} {seq} is Passed', level='info')
                    res.append(1)
                elif code == "" and error_code != "" and stat["status"] != 0:
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
                                if stat[key][d].get("status") == error_code \
                                        or stat[key][d].get("code") == error_code:
                                    # 列表中每一个元素都是字典类型，取字典中关键字"status"对应的错误码，用来做判断
                                    log(f'[Match ErrorCode: {error_code} is OK!] TestCase {seq} is Passed',
                                        level='info')
                                    res.append(1)
                                    # 如果错误码和预期一致，目前遇到的返回码只涉及到关键字"errors"or"addErrors"or"delErrors"
                                    # or"updateErrors"中的一种，所以一旦找到就退出循环
                                    break
                            else:
                                log(f'[Not Match ErrorCode: {error_code}] TestCase {seq} is Failed',
                                    level='error')
                                res.append(0)
                                # 整个错误码对应列表中的字典元素都和预期错误码不一致，记为测试fail
                        elif (key == 'result') and isinstance(stat[key], dict):
                            # 用于user->"用户账号批量导入"测试判断
                            # {"status":4,"result":{"count":4,"errors":[{"index":5,"code":251},{"index":6,"code":252},
                            # {"index":7,"code":252},{"index":8,"code":252}]}}
                            if stat[key]['count'] == error_code or \
                                    ('errors' in stat[key] and error_code == 'errors'):
                                # 判断count或者errors是否与错误检查点一致
                                log(f'[Match ErrorCode: {error_code} is OK!] TestCase {seq} is Passed',
                                    level='info')
                                res.append(1)
                            else:
                                for b in range(len(stat[key]['errors'])):
                                    # 遍历关键字为"errors"的字典所对应值的列表，这里列表所对应的元素个数是变化的
                                    if stat[key]['errors'][b].get("index") == error_code \
                                            or stat[key]['errors'][b].get("code") == error_code:
                                        # 列表中每一个元素都是字典类型，取字典中关键字"index"或者“code”对应的错误码，用来做判断
                                        log(f'[Match ErrorCode: {error_code} is OK!] TestCase {seq} is Passed',
                                            level='info')
                                        res.append(1)
                                        # 如果错误码和预期一致，目前遇到的返回码只涉及到关键字"code"or"index"中的一种，
                                        # 所以一旦找到就退出循环
                                        break
                                else:
                                    log(f'[Not Match ErrorCode: {error_code}] TestCase {seq} is Failed',
                                        level='error')
                                    res.append(0)
                                    # 整个错误码对应列表中的字典元素都和预期错误码不一致，记为测试fail
                        elif (key == 'result') and not isinstance(stat[key], dict):
                            # org->组织机构导入-IP格式不正确{"status":3,"result":null}
                            log(f'[Not Match ErrorCode: {error_code}] TestCase {seq} is Failed',
                                level='error')
                            res.append(0)

                elif code == "" and stat["status"] == 0:
                    log(f'[The Reason for TestCase {seq} Failure is function problem', level='error')
                    res.append(0)
                else:
                    log(
                        f'\n[结果]:\n'
                        f"> [Except Code: {str(code).strip('.0')} ] | [Actual Code: {stat['status']}] "
                        f"TestCase {name}({seq}) is Failed",
                        level='error')
                    res.append(0)
        return res
