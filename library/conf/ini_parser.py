#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# ini_parser.py - ini文件解析
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
#       - 2018/10/11 14:27  add by yanwh
#
# *********************************************************************
"""
copy from https://github.com/BNMetrics/bnmetrics-utils/tree/master/bnmutils by yanwh
针对具体的项目进行了扩展和增强,使其能够支持.方式访问
"""
import os
import ast
from functools import wraps
from contextlib import contextmanager

from typing import Iterable, Union, List, Callable

from configparser import RawConfigParser as BuiltinConfigParser


class InvalidConfig(Exception):
    pass


class InvalidConfigOption(Exception):
    pass


def doc_parametrize(**parameters) -> Callable:
    """
    Decorator for allowing parameters to be passed into docstring
    :param parameters: key value pair that corresponds to the params in docstring
    """

    def decorator_(callable_):
        new_doc = callable_.__doc__.format(**parameters)
        callable_.__doc__ = new_doc

        @wraps(callable_)
        def wrapper(*args, **kwargs):
            return callable_(*args, **kwargs)

        return wrapper

    return decorator_


@contextmanager
def cd(dir_path: str):
    """
    Context manager for cd, change back to original directory when done
    """
    cwd = os.getcwd()
    try:
        os.chdir(os.path.expanduser(dir_path))
        yield
    finally:
        os.chdir(cwd)


def strip_blank_recursive(nested_list: list, evaluate: bool = False):
    """
    Strip blank space or newline characters recursively for a nested list
    *This updates the original list passed in*
    """
    if not isinstance(nested_list, list):
        raise ValueError(f"iterable passed must be type of list. not '{type(nested_list).__name__}'")

    for i, v in enumerate(nested_list):
        if isinstance(v, list):
            strip_blank_recursive(v, evaluate)
        elif isinstance(v, str):
            if not evaluate:
                val_ = v.strip()
            else:
                val_ = str_eval(v)

            nested_list[i] = val_


def str_eval(parse_str: str):
    """
    Evaluate string, return the respective object if evaluation is successful,
    """
    try:
        val = ast.literal_eval(parse_str.strip())
    except (ValueError, SyntaxError):  # SyntaxError raised when passing in "{asctime}::{message}"
        val = parse_str.strip()

    return val


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
        # from box import Box
        # return Box(config_dict)

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
