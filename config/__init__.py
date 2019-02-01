#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# __init__.py
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
#       - 2019/1/29 10:17  add by yanwh
#
# *********************************************************************
"""
module doc string
"""
from pathlib import Path

from library.loader import Config


def complex_path_config(name, dot_style=False):
    """根据名称提取config文件下面的配置文件"""
    return Config(f'{Path(__file__).parent}/{name}', dot_style=dot_style)


user = complex_path_config('user.yaml')
service = complex_path_config('service.yaml')
settings = complex_path_config('settings.ini')
testcase = complex_path_config('testcase.ini')
route = complex_path_config('route.yaml')
system_init = complex_path_config('systeminit.yaml', dot_style=True)



x= system_init['init_root_org_net']['request']['rootOrgName']
exec(x)
# import yaml
#
# class folded_unicode(str): pass
# class literal_unicode(str): pass
#
# def folded_unicode_representer(dumper, data):
#     return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
# def literal_unicode_representer(dumper, data):
#     return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
#
# yaml.add_representer(folded_unicode, folded_unicode_representer)
# yaml.add_representer(literal_unicode, literal_unicode_representer)
#
# data = {
#     'literal':literal_unicode(
#         u'by hjw              ___\n'
#          '   __              /.-.\\\n'
#          '  /  )_____________\\\\  Y\n'
#          ' /_ /=== == === === =\\ _\\_\n'
#          '( /)=== == === === == Y   \\\n'
#          ' `-------------------(  o  )\n'
#          '                      \\___/\n'),
#     'folded': folded_unicode(
#         u'It removes all ordinary curses from all equipped items. '
#         'Heavy or permanent curses are unaffected.\n')}
#
# print(yaml.dump(data))