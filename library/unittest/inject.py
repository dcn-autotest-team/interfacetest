#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# inject.py - 元类，用户对unittest进行注入的模块
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
#       - 2018/9/30 17:09  add by yanwh
#
# *********************************************************************
import functools
import time
import unittest

from library.conf import settings as const
from library.log import log
Tag = const.Tag
CASE_TAG_FLAG = "__case_tag__"
CASE_DATA_FLAG = "__case_data__"
CASE_DATA_UNPACK_FLAG = "__case_data_unpack__"
CASE_ID_FLAG = "__case_id__"
CASE_INFO_FLAG = "__case_info__"
CASE_SKIP_FLAG = "__unittest_skip__"
CASE_SKIP_REASON_FLAG = "__unittest_skip_why__"

__all__ = ["skip", "skip_if", "data", "tag", "stop_patch", "Tag"]


def skip(reason):
    def wrap(func):
        return unittest.skip(reason)(func)

    return wrap


def skip_if(condition, reason):
    def wrap(func):
        return unittest.skipIf(condition, reason)(func)

    return wrap


def data(*values, unpack=True):
    """注入测试数据，可以做为测试用例的数据驱动
    1. 单一参数的测试用例
    @data(10001, 10002, 10003)
    def test_receive_bless_box(self, box_id):
        print(box_id)

    2. 多个参数的测试用例
    @data(["gold", 100], ["diamond", 500])
    def test_bless(self, bless_type, award):
        print(bless_type)
        print(award)

    3. 是否对测试数据进行解包
    @data({"gold": 1000, "diamond": 100}, {"gold": 2000, "diamond": 200}, unpack=False)
    def test_get_battle_reward(self, reward):
        print(reward)
        print("获得的钻石数量是：{}".format(reward['diamond']))

    :param values:测试数据
    :param unpack: 是否解包
    :return:
    """

    def wrap(func):
        if hasattr(func, CASE_DATA_FLAG):
            log("{}的测试数据只能初始化一次".format(func.__name__), level='error')
        setattr(func, CASE_DATA_FLAG, values)
        setattr(func, CASE_DATA_UNPACK_FLAG, unpack)
        return func

    return wrap


def tag(*tag_type):
    """指定测试用例的标签，可以作为测试用例分组使用，用例默认会有Tag.FULL标签，支持同时设定多个标签，如：
    @tag(Tag.SP, Tag.FULL)
    def test_func(self):
        pass

    :param tag_type:标签类型，在case_tag.py里边自定义
    :return:
    """

    def wrap(func):
        if not hasattr(func, CASE_TAG_FLAG):
            tags = {const.Tag.FULL}
            tags.update(tag_type)
            setattr(func, CASE_TAG_FLAG, tags)
        else:
            getattr(func, CASE_TAG_FLAG).update(tag_type)
        return func

    return wrap


def _handler(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        time.sleep(const.EXECUTE_INTERVAL)
        msg = "start to test {} ({}/{})".format(getattr(func, CASE_INFO_FLAG),
                                                getattr(func, CASE_ID_FLAG),
                                                Tool.total_case_num)
        log(msg, level='info')
        result = func(*args, **kwargs)
        return result

    return wrap


class Tool:
    total_case_num = 0

    @classmethod
    def general_case_id(cls):
        cls.total_case_num += 1
        return cls.total_case_num

    @staticmethod
    def modify_raw_func_name_to_sort_case(raw_func_name, raw_func):
        case_id = Tool.general_case_id()
        setattr(raw_func, CASE_ID_FLAG, case_id)
        if const.SORT_CASE:
            func_name = raw_func_name.replace("test_", "test_{:05d}_".format(case_id))
        else:
            func_name = raw_func_name
        return func_name

    @staticmethod
    def general_case_name_with_test_data(func_name, index, test_data):
        if const.FULL_CASE_NAME:
            params_str = "_".join([str(_) for _ in test_data]).replace(".", "")
            func_name += "_{:05d}_{}".format(index, params_str)
        else:
            func_name += "_{:05d}".format(index)
        if len(func_name) > const.MAX_CASE_NAME_LEN:
            func_name = func_name[:const.MAX_CASE_NAME_LEN] + "……"
        return func_name

    @staticmethod
    def create_case_with_case_data(raw_func_name, raw_func):
        result = dict()
        for index, test_data in enumerate(getattr(raw_func, CASE_DATA_FLAG), 1):
            func_name = Tool.modify_raw_func_name_to_sort_case(raw_func_name, raw_func)

            if isinstance(test_data, list):
                func_name = Tool.general_case_name_with_test_data(func_name, index, test_data)
                if getattr(raw_func, CASE_DATA_UNPACK_FLAG, None):
                    result[func_name] = _handler(_feed_data(*test_data)(raw_func))
                else:
                    result[func_name] = _handler(_feed_data(test_data)(raw_func))

            elif isinstance(test_data, dict):
                func_name = Tool.general_case_name_with_test_data(func_name, index, test_data.values())
                if getattr(raw_func, CASE_DATA_UNPACK_FLAG, None):
                    result[func_name] = _handler(_feed_data(**test_data)(raw_func))
                else:
                    result[func_name] = _handler(_feed_data(test_data)(raw_func))

            elif isinstance(test_data, (int, str, bool, float)):
                func_name = Tool.general_case_name_with_test_data(func_name, index, [test_data])
                result[func_name] = _handler(_feed_data(test_data)(raw_func))

            else:
                raise Exception("无法解析{}".format(test_data))
        return result

    @staticmethod
    def create_case_without_case_data(raw_func_name, raw_func):
        result = dict()
        func_name = Tool.modify_raw_func_name_to_sort_case(raw_func_name, raw_func)
        if len(func_name) > const.MAX_CASE_NAME_LEN:
            func_name = func_name[:const.MAX_CASE_NAME_LEN] + "……"
        result[func_name] = _handler(raw_func)
        return result

    @staticmethod
    def filter_test_case(funcs_dict):
        funcs = dict()
        cases = dict()
        for i in funcs_dict:
            if i.startswith("test_"):
                cases[i] = funcs_dict[i]
            else:
                funcs[i] = funcs_dict[i]

        return funcs, cases.items()


def _feed_data(*args, **kwargs):
    def wrap(func):
        @functools.wraps(func)
        def _wrap(self):
            return func(self, *args, **kwargs)

        return _wrap

    return wrap


class Meta(type):
    # noinspection PyInitNewSignature
    def __new__(mcs, name, bases, attr):
        funcs, cases = Tool.filter_test_case(attr)
        for raw_case_name, raw_case in cases:
            if not hasattr(raw_case, CASE_TAG_FLAG):
                setattr(raw_case, CASE_TAG_FLAG, {const.Tag.SMOKE, const.Tag.FULL})  # 没有指定tag的用例，默认有SMOKE和FULL标记

            # 注入用例信息
            case_info = "{}.{}".format(raw_case.__module__, raw_case.__name__)
            setattr(raw_case, CASE_INFO_FLAG, case_info)

            # 检查用例描述
            if const.CHECK_CASE_DOC and not raw_case.__doc__:
                log("{}没有用例描述".format(case_info), level='warning')

            # 过滤不执行的用例
            if not getattr(raw_case, CASE_TAG_FLAG) & set(const.RUN_CASE):
                continue

            # 注入测试数据
            if hasattr(raw_case, CASE_DATA_FLAG):
                funcs.update(Tool.create_case_with_case_data(raw_case_name, raw_case))
            else:
                funcs.update(Tool.create_case_without_case_data(raw_case_name, raw_case))

        return super(Meta, mcs).__new__(mcs, name, bases, funcs)


class _TestCase(unittest.TestCase, metaclass=Meta):
    def shortDescription(self):
        """覆盖父类的方法，获取函数的注释

        :return:
        """
        doc = self._testMethodDoc
        doc = doc and doc.split()[0].strip() or None
        return doc


raw_unittest_testcase = unittest.TestCase
unittest.TestCase = _TestCase


def stop_patch():
    unittest.TestCase = raw_unittest_testcase
