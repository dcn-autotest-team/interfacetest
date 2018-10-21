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
针对具体的项目进行了扩展和增强,使其能够支持.方式访问
"""
import csv
import io
import json
import os
from configparser import ExtendedInterpolation, RawConfigParser as BuiltinConfigParser
from json import JSONDecodeError
from typing import Iterable, List, Union

from library.exceptions import FileFormatError, FileNotFound, InvalidConfig, InvalidConfigOption
from library.file import assert_file
from library.log import log
from library.utils import str_eval, strip_blank_recursive


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
        :param section:
        :param option:
        :return:
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
        Map the configuration option to dict.
        * Do not pass in the whole config section!*
        :param: parse_option: values from config.get('section', 'option')
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
        Converting the ConfigParser *section* to a dictionary format
        :param config_section: values from config.items('section') or dict(config['section'])
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
        flatten nested dict config options for configuration file *sections*
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
    """ check file format if valid
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
    加载ini文件，并对内容进行检查
    :param ini_file:
    :return: dict
    """
    ini_content = ConfigParser.from_files(ini_file, interpolation=ExtendedInterpolation(), strict=True).to_dict()
    _check_format(ini_file, ini_content)
    return ini_content


load_conf_file = load_properties_file = load_ini_file


def load_json_file(json_file):
    """
    加载json文件，并对内容进行检查
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


def load_env_file(dot_env_path):
    """ load .env file.
    Args:
        dot_env_path (str): .env file path
    Returns:
        dict: environment variables mapping
            {
                "UserName": "yanwh",
                "Password": "123456",
                "PROJECT_KEY": "ABCDEFGH"
            }
    Raises:
        exceptions.FileFormatError: If .env file format is invalid.
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
    """ load csv file and check file content format
    @param
        csv_file: csv file path
        e.g. csv file content:
            username,password
            test1,111111
            test2,222222
            test3,333333
    @return
        list of parameter, each parameter is in dict format
        e.g.
        [
            {'username': 'test1', 'password': '111111'},
            {'username': 'test2', 'password': '222222'},
            {'username': 'test3', 'password': '333333'}
        ]
    """
    csv_content_list = []

    with io.open(csv_file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_content_list.append(row)

    return csv_content_list


# def load_py_file(py_file):
#     try:
#
#         return importlib.import_module(py_file.__fspath__())
#     except (ImportError, TypeError):
#         return load_py_from_filename(py_file)
#
#
# def load_py_from_filename(filename):
#     """
#     导入文件
#     :param filename:
#     :return:
#     """
#     filename = assert_file(filename)
#     if not filename.suffix == '.py':
#         filename = '{0}.py'.format(filename)
#
#     mod = types.ModuleType(filename.stem)
#     mod.__file__ = filename
#     try:
#         with io.open(
#                 find_file(filename),
#                 encoding=const.ENCODING
#         ) as config_file:
#             exec(
#                 compile(config_file.read(), filename, 'exec'),
#                 mod.__dict__
#             )
#     except IOError as e:
#         err_msg = f'加载py文件遇到错误({e.strerror} {filename})\n'
#         log(err_msg, level='error')
#     return mod


def load_file(file_path):
    """
    根据传入文件名称后缀动态获取对应解析函数解析出来的内容
    支持解析.env, json, csv, ini等
    :param file_path:
    :return:
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
    """ set variables mapping to os.environ
    """
    for variable in variables_mapping:
        os.environ[variable] = variables_mapping[variable]
        log("Loaded variable: {}".format(variable))


