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
#       - 2018/8/10 17:05  add by wangxinae
#
# *********************************************************************
from __future__ import print_function, unicode_literals

import unittest

from interfacetest.testcase.helper import run


class TestSysSet(unittest.TestCase):
    @run()
    def test_cpu_status(self):
        pass

    @run()
    def test_get_sys_info(self):
        pass

    @run()
    def test_set_sys_info(self):
        pass

    @run()
    def test_get_configs(self):
        pass

    @run()
    def test_get_config(self):
        pass

    @run()
    def test_update_config(self):
        pass

    @run()
    def test_ping(self):
        pass

    @run()
    def test_get_license(self):
        pass

    @run()
    def test_add_license(self):
        pass

    @run()
    def test_reboot_system(self):
        pass

    @run()
    def test_init(self):
        pass

    @run()
    def test_get_sys_time(self):
        pass

    @run()
    def test_set_time(self):
        pass

    @run()
    def test_get_version(self):
        pass

    @run()
    def test_add_vendor(self):
        pass

    @run()
    def test_sms_config(self):
        pass

    @run()
    def test_upgrade(self):
        pass

    @run()
    def test_backup_to_client(self):
        pass

    @run()
    def test_backup_to_server(self):
        pass

    @run()
    def test_backup(self):
        pass

    @run()
    def test_backup_param(self):
        pass

    @run()
    def test_backup_list(self):
        pass

    @run()
    def test_backup_export(self):
        pass

    @run()
    def test_backup_del(self):
        pass

    @run()
    def test_restore1(self):
        pass

    @run()
    def test_restore2(self):
        pass

    @run()
    def test_network_param(self):
        pass

    @run()
    def test_get_network_param(self):
        pass
