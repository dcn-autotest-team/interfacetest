#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# loader.py -
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
#       - 2018/9/3 17:26  add by yanwh
#
# *********************************************************************
"""
+ 模块说明：
    loader模块主要用于将json/ini/csv/env文件读取到内存中，提供给python程序进行读写操作
    同时对ini文件进行了扩展使得读取出来的内容不在全是字符串，而是进行了适当的转义操作，例如
    例如对于ini中想表达成字典/元祖/列表/bool类型的字符串均转换成了对应的类型，json是利用
    自带的json库进行转换，csv读取出来的是k-v键值对组成的list，env文件读取将读取出来的k，v
    字符串转换成对应的字典。

"""
import csv
import io
import json
import os
import sys
from configparser import ExtendedInterpolation, RawConfigParser as BuiltinConfigParser
from json import JSONDecodeError
from typing import Iterable, List, Union

import toml
import yaml.parser

from library.exceptions import FileFormatError, FileNotFound, InvalidConfig, InvalidConfigOption
from library.file import assert_file
from library.log import log
from library.utils import str_eval, strip_blank_recursive, DcnDict


class ConfigParser(BuiltinConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preserve casing for options
        self.optionxform = str

    # noinspection PyTypeChecker
    @classmethod
    def from_files(cls, file_names: Union[str, os.PathLike, Iterable],
                   encoding='utf-8', *args, **kwargs):

        # Transforming file_names into string format to work with older versions of python,  e.g. python 3.6.0
        if isinstance(file_names, Iterable) and \
                not isinstance(file_names, str):
            file_names = [str(i) for i in file_names]

        obj = cls(*args, **kwargs)
        obj.read(file_names, encoding=encoding)

        if not obj.sections():
            raise InvalidConfig(f"Invalid config file/files: {file_names}.")

        return obj

    @classmethod
    def from_dict(cls, parse_dict: dict, *args, **kwargs):
        obj = cls(*args, **kwargs)

        flattened_dict = {}

        for section, val in parse_dict.items():
            flattened_dict[section] = obj._flatten_section_dict(val)

        obj.read_dict(flattened_dict)

        return obj

    def to_dict(self, section: str = None, option: str = None, **kwargs):
        """
        + 说明：
            将配置文件转换成字典

        :param section: 配置文件的section
        :param option: 配置文件的option
        :return: 字典
        """
        if option and not section:
            raise ValueError("Option cannot be passed on its own.")

        if section and option:
            option_str = self.get(section, option)
            return self._option_to_dict(option_str)

        if section:
            section_list = self.items(section, **kwargs)
            return self._section_to_dict(section_list)

        config_dict = {}
        for i in self.sections():
            config_dict[i] = self._section_to_dict(self.items(i))
        return config_dict

    @staticmethod
    def _option_to_dict(parse_option: str) -> dict:
        """
        + 说明：
            将option转换成字典

        :param parse_option: 通过config.get('section', 'option')获取的值
        """
        try:
            str_split = parse_option.strip().split('\n')  # raise AttributeError
            mapped_list = list(map(lambda x: x.split(':', 1), str_split))

            strip_blank_recursive(mapped_list, evaluate=True)

            return dict(mapped_list)  # raises ValueError
        except AttributeError:
            raise InvalidConfigOption(f"option passed must be a string value, "
                                      f"not type of '{type(parse_option).__name__}'.")
        except ValueError:
            if '\n' not in parse_option:
                raise ValueError(f"'{parse_option}' cannot be converted to dict. alternatively, "
                                 f"use ConfigParser.get(section, value) to get the value.")

            raise InvalidConfigOption(f"{parse_option} is not a valid option, "
                                      f"please follow the convention of 'key: value'")

    def _section_to_dict(self, config_section: Union[List[tuple], dict]) -> dict:
        """
        + 说明：
            将section转换成字典

        :param config_section: 通过config.items('section')or dict(config['section'])获取的值

        """
        if isinstance(config_section, dict):
            return {k: self._option_to_dict(v) if '\n' in v else str_eval(v)
                    for k, v in config_section.items()}

        if isinstance(config_section, list):
            return {i[0]: self._option_to_dict(i[1]) if '\n' in i[1] else str_eval(i[1])
                    for i in config_section}

        raise ValueError(f"Invalid section type '{type(config_section).__name__}'")

    @staticmethod
    def _flatten_section_dict(parse_dict: dict):
        """
        + 说明：
            将嵌套的配置文件sections字典进行扁平化遍历处理

        """
        flattened = {}

        for k, v in parse_dict.items():

            if isinstance(v, dict):
                val_list = [f'{k1}: {v1}' for k1, v1 in v.items()]

                str_val = '\n' + '\n'.join(val_list)
            else:
                str_val = str(v)

            flattened[k] = str_val

        return flattened


def _check_format(file_path, content):
    """
    检查文件格式是否有效
    """
    if not content:
        # 解析出来文件内容为空
        err_msg = f'从{file_path}中解析出来的内容为空'
        log(err_msg, 'error')
        raise FileFormatError(err_msg)

    elif not isinstance(content, (list, dict)):
        err_msg = f'从{file_path}中解析出来的内容格式不正确'
        log(err_msg, 'error')
        raise FileFormatError(err_msg)


def load_ini_file(ini_file):
    """
    + 说明：
        加载ini文件，并对内容进行检查

    :param ini_file: 配置文件路径
    :return: 配置文件内容(dict)

    """
    if hasattr(ini_file, '__fspath__'):
        ini_file = ini_file.__fspath__()

    ini_content = ConfigParser.from_files(ini_file, interpolation=ExtendedInterpolation(),
                                          strict=True).to_dict()
    _check_format(ini_file, ini_content)
    return ini_content


load_conf_file = load_properties_file = load_ini_file


def load_json_file(json_file):
    """
    + 说明：
        加载json文件，并对内容进行检查

    :param json_file: 配置文件路径
    :return: 配置文件内容(dict)

    """
    with io.open(json_file, encoding='utf-8') as data_file:
        try:
            json_content = json.load(data_file)
        except JSONDecodeError:
            err_msg = u"JSONDecodeError: JSON file format error: {}".format(json_file)
            log(err_msg, 'error')
            raise FileFormatError(err_msg)

        _check_format(json_file, json_content)
        return json_content


def load_yaml_file(yaml_file, dot_style=False):
    """
    + 说明：
        加载yaml文件，并对内容进行检查

    :param dot_style: dict转换成能够通过.方式进行访问
    :param yaml_file: 配置文件路径
    :return: 配置文件内容(dict)

    """
    with open(yaml_file, encoding='utf-8') as data_file:
        try:
            yaml_content = yaml.load(data_file)
        except yaml.parser.ParserError:
            err_msg = f"YAMLParserError: YAML file format error: {yaml_file}"
            log(err_msg, 'error')
            raise FileFormatError(err_msg)

        _check_format(yaml_file, yaml_content)
        if dot_style:
            yaml_content = DcnDict(yaml_content)
        return yaml_content


load_yml_file = load_yaml_file


def load_toml_file(toml_file):
    """
    + 说明：
        加载toml文件，并对内容进行检查

    :param toml_file: 配置文件路径
    :return: 配置文件内容(dict)

    """
    with open(toml_file, encoding='utf-8') as data_file:
        try:
            toml_file_content = toml.load(data_file)
        except yaml.parser.ParserError:
            err_msg = f"YAMLParserError: YAML file format error: {toml_file}"
            log(err_msg, 'error')
            raise FileFormatError(err_msg)

        _check_format(toml_file, toml_file_content)
        return toml_file_content


def load_env_file(dot_env_path):
    """
    + 说明：
        加载env文件内容

    :param dot_env_path: dot_env_path
    :return: 将env文件中的内容设置到env中同时返回读取的内容

    """
    if not os.path.isfile(dot_env_path):
        raise FileNotFound(".env file path is not exist.")

    log("Loading environment variables from {}".format(dot_env_path), 'info')
    env_variables_mapping = {}
    with io.open(dot_env_path, 'r', encoding='utf-8') as fp:
        for line in fp:
            if "=" in line:
                variable, value = line.split("=", 1)
            elif ":" in line:
                variable, value = line.split(":", 1)
            else:
                raise FileFormatError(".env format error")

            env_variables_mapping[variable.strip()] = value.strip()

    set_os_environ(env_variables_mapping)
    return env_variables_mapping


def load_csv_file(csv_file):
    """
    + 说明：
        加载csv_file内容

    +　用法：
        csv文件内容如下：

            username,password

            test1,111111

            test2,222222

            test3,333333

        返回值如下：

        [

        {'username': 'test1', 'password': '111111'},

        {'username': 'test2', 'password': '222222'},

        {'username': 'test3', 'password': '333333'}

        ]

    :param csv_file:  csv file path
    :return: [ {key1:val1}, {key2:val2} ]
    """

    csv_content_list = []

    with io.open(csv_file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_content_list.append(row)

    return csv_content_list


def load_file(file_path):
    """
    +说明：
        根据传入文件名称后缀动态获取对应解析函数解析出来的内容，
        支持解析.env, json, csv, ini等。

    :param file_path: 要解析文件路径
    :return: 文件内容

    """
    file_path = assert_file(file_path)
    try:
        if file_path.name == '.env':
            return load_env_file(file_path)
        return globals()[f'load_{file_path.suffix[1:].lower()}_file'](file_path)  # 利用模块的globals()获取模块字典，从中
        #  根据file_path后缀匹配对应函数
    except KeyError:
        err_msg = f'不支持文件类型 {file_path}'
        log(err_msg, level='warning')


def set_os_environ(variables_mapping):
    """
    +　说明：
        将变量字典映射表设置到os.environ中去

    :param variables_mapping: 要设置到环境变量中的字典
    :return: 文件内容
    """
    for variable in variables_mapping:
        os.environ[variable] = variables_mapping[variable]
        log("Loaded variable: {}".format(variable))


class Config(object):
    """
    读取配置文件
    注意:
      1、优先读取当前目录下, 第二顺序读取项目根目录下
      2、同一名称配置文件只加载一次,再次实例化不再加载

    使用:
    from pithy import Config
    config = Config()  # 使用默认配置文件名settings.yaml
    config = Config('pithy.yaml')  # 使用自定义配置文件

    print config['pithy_db']['host']  # 取值
    ...

    """
    config_object_instance = {}

    def __new__(cls, file_name='settings.yaml', dot_style=False):
        if file_name not in cls.config_object_instance:
            config_file_path = file_name
            if not os.path.exists(file_name):
                config_file_path0 = os.path.join(sys.path[0], file_name)
                config_file_path1 = os.path.join(sys.path[1], file_name)
                if os.path.exists(config_file_path0):
                    config_file_path = config_file_path0
                elif os.path.exists(config_file_path1):
                    config_file_path = config_file_path1
                else:
                    raise OSError('can not find config file !')
            if file_name.endswith(('.yaml', '.yml')):
                cls.config_object_instance[file_name] = load_yaml_file(config_file_path, dot_style=dot_style)
            elif file_name.endswith(('.cfg', '.ini', '.conf', '.properties')):
                cls.config_object_instance[file_name] = load_ini_file(config_file_path)
            elif file_name.endswith('.json'):
                cls.config_object_instance[file_name] = load_json_file(config_file_path)
            elif file_name.endswith(('.toml', 'tml')):
                cls.config_object_instance[file_name] = load_toml_file(config_file_path)
            elif file_name.endswith('.csv'):
                cls.config_object_instance[file_name] = load_csv_file(config_file_path)
            elif file_name.endswith('.env'):
                cls.config_object_instance[file_name] = load_env_file(config_file_path)
            else:
                raise ValueError('Unsupported configuration file type')

        return cls.config_object_instance[file_name]

    def __getitem__(self, item):
        return self[item]
