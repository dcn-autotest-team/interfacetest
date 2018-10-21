#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# base.py - 
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
#       - 2018/10/18 9:44  add by yanwh
#
# *********************************************************************
import ast
import importlib
import json
import os
from pathlib import Path

import copy

from library.conf import global_settings
from library.decorator import SingletonMeta
from library.lazy import LazyObject, empty


__all__ = ('ConfigParser', 'settings')

ENVIRONMENT_VARIABLE = "DCN_SETTINGS_MODULE"

true_values = (
    't', 'true', 'enabled', '1', 'on', 'yes', 'True'
)

false_values = (
    'f', 'false', 'disabled', '0', 'off', 'no', 'False', ''
)

converters = {
    '@int': int,
    '@float': float,
    '@bool': (
        lambda value: True if str(value).lower() in true_values else False
    ),
    '@json': json.loads,
    '@eval': ast.literal_eval,
    '@path': Path,
    # 保留特殊的占位符，运算的时候返回None
    '@note': lambda value: None,
    '@comment': lambda value: None,
    '@null': lambda value: None,
    '@none': lambda value: None,
}


def parse_conf_data(data):
    def _parse_conf_data():
        """
        @int @bool @float @json (相当于list和dict)
        string不做转换
        """
        nonlocal data

        if data and isinstance(data, str) and data.startswith(tuple(converters.keys())):
            parts = data.partition(' ')
            converter_key = parts[0]
            value = parts[-1]
            return converters.get(converter_key)(value)

        return data

    if isinstance(data, (tuple, list)):
        # 递归处理sequence序列(list tuple)
        return [parse_conf_data(item) for item in data]
    elif isinstance(data, dict):
        # 递归处理字典
        _parsed = {}
        for k, v in data.items():
            _parsed[k] = parse_conf_data(v)
        return _parsed
    else:
        # 处理字符串
        return _parse_conf_data()


class DcnDict(dict):
    """
    invoke from https://github.com/mewwts/addict/blob/master/addict/addict.py
    增强版支持递归创建和引用
        >>> body = {
        ...                'query': {
        ...                    'filtered': {
        ...                        'query': {
        ...                            'match': {'description': 'addictive'}
        ...                        },
        ...                        'filter': {
        ...                            'term': {'created_by': 'Mats'}
        ...                        }
        ...                    }
        ...                }
        ...            }
        >>> body = DcnDict()
        >>> body.query.filtered.query.match.description = 'addictive'
        >>> body.query.filtered.filter.term.created_by = 'Mats'

        >>> o = DcnDict(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """

    # noinspection PyMethodParameters,PyMissingConstructor
    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, '__parent', kwargs.pop('__parent', None))
        object.__setattr__(__self, '__key', kwargs.pop('__key', None))
        for _arg in args:
            if not _arg:
                continue
            elif isinstance(_arg, dict):
                for key, val in _arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(_arg, tuple) and (not isinstance(_arg[0], tuple)):
                __self[_arg[0]] = __self._hook(_arg[1])
            else:
                for key, val in iter(_arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        super(DcnDict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __missing__(self, name):
        return self.__class__(__parent=self, __key=name)

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    def update(self, *args, **kwargs):
        other = {}
        if args:
            if len(args) > 1:
                raise TypeError()
            other.update(args[0])
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or
                    (not isinstance(self[k], dict)) or
                    (not isinstance(v, dict))):
                self[k] = v
            else:
                self[k].update(v)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def __repr__(self):
        return '<DcnDict ' + dict.__repr__(self) + '>'


class LazySettings(LazyObject, metaclass=SingletonMeta):
    def __init__(self, **kwargs):
        """
        处理用户配置初始化

        :param kwargs: 用于覆盖global_settings中的值
        """
        for k, v in kwargs.items():
            setattr(global_settings, k.upper(), v)
        super(LazySettings, self).__init__()

    def _setup(self, name=None):
        """只运行一次的初始化配置，如果环境变量中设置了settings_module则从中加载"""
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)  # 提供从环境变量中加载配置
        self._wrapped = Settings(
            settings_module=settings_module
        )

    def __getattr__(self, name):
        """允许通过settings.attr的方式访问Settings实例中的方法和属性,同时LazySettings缓存一份"""
        if self._wrapped is empty:
            self._setup()

        return getattr(self._wrapped, name)

    def __call__(self, *args, **kwargs):
        """允许通过self()的方式替换self.get
        """
        return self.get(*args, **kwargs)

    def __repr__(self):
        if self._wrapped is empty:
            return '<LazySettings [Unevaluated]>'
        return '<LazySettings "%(settings_module)s">' % {
            'settings_module': self._wrapped.SETTINGS_MODULE,
        }

    def configure(self, default_settings=global_settings, **options):
        """
        Called to manually configure the settings. The 'default_settings'
        parameter sets where to retrieve any unspecified values from (its
        argument must support attribute access (__getattr__)).
        """
        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')
        user_settings = UserSettings(default_settings)
        for name, value in options.items():
            setattr(user_settings, name, value)
        self._wrapped = user_settings

    @property
    def configured(self):
        """判断wrapped是否已经配置"""
        return self._wrapped is not empty


class Settings(object):
    def __init__(self, settings_module):
        """
        默认设置，先加载global_settings然后加载用户配置（后者覆盖前者）
        :param settings_module:
        """
        # self._fresh = False
        self._store = {}
        self._deleted = set()
        self.SETTINGS_MODULE = settings_module
        for setting in dir(global_settings):
            from enum import Enum
            from inspect import isclass
            if setting.isupper() or (isclass(getattr(global_settings, setting)) and issubclass(getattr(global_settings,
                                                                                                       setting), Enum)):
                self.set(setting, getattr(global_settings, setting))

        if settings_module:
            mod = importlib.import_module(settings_module)
            for setting in dir(mod):
                if setting.isupper():
                    setting_value = getattr(mod, setting)
                    self.set(setting, setting_value)

    def __call__(self, *args, **kwargs):
        """允许通过self()的方式替换self.get
        """
        return self.get(*args, **kwargs)

    def __setattr__(self, name, value):
        """支持self.name = value"""
        try:
            self._deleted.discard(name)
        except AttributeError:
            pass

        super(Settings, self).__setattr__(name, value)

    def __getitem__(self, item):
        """支持self['KEY']`"""
        value = self.get(item)
        if value is None:
            raise KeyError('{0} does not exists'.format(item))
        return value

    def __setitem__(self, key, value):
        """支持self['KEY'] = 'value'`"""
        self.set(key, value)

    def __delattr__(self, name):
        """支持del"""
        self._deleted.add(name)
        if hasattr(self, name):
            super(Settings, self).__delattr__(name)

    def __iter__(self):
        """支持iter协议"""
        return iter(self.store.items())

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }

    def __str__(self):
        from pprint import pprint
        pprint(self.store)
        return ''

    def format(self):
        from pprint import pformat
        return pformat(self.store)

    @property
    def store(self):
        """获取内部存储内容"""
        return self._store

    def get(self, key, default=None, cast=None):
        """
        优先选用get方式对值进行获取操作
        :param key: 要获取的值的key
        :param default: 如果通过key找不到，设置默认值
        :param cast: 类型转换 @int, @float, @bool or @json or @path
        :return: The value if found, default or None
        """
        key = key
        if key in self._deleted:
            return default

        data = self.store.get(key, default)
        if cast:
            data = converters.get(cast)(data)
        return data

    def set(self, key, value):
        """优先选用的设置值的方式

        :param key: The key to store
        :param value: The value to store
        """
        value = parse_conf_data(value)

        key = key.strip()
        if key in self.store and value != self.store[key]:
            from library.log import log
            log(f'注意 {key} {self(key)} 修改成 {key} {value}', level='warning')
        setattr(self, key, value)
        self.store[key] = value
        self._deleted.discard(key)

    def update(self, data=None, **kwargs):
        """
        更新操作
        :param data: Data to be updated
        :param kwargs: extra values to update
        :return: None
        """
        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            self.set(key, value)

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def exists(self, key):
        """检查key是否存在

        :param key: the name of setting variable
        :return: Boolean
        """
        key = key.upper()
        if key in self._deleted:
            return False
        return key in self.store

    def as_bool(self, key):
        """Partial method for get with bool cast"""
        return self.get(key, cast='@bool')

    def as_int(self, key):
        """Partial method for get with int cast"""
        return self.get(key, cast='@int')

    def as_float(self, key):
        """Partial method for get with float cast"""
        return self.get(key, cast='@float')

    def as_json(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast='@json')

    def as_path(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast='@path')

    def as_eval(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast='@eval')


# -----------------------------------------------------------------------------------------------------------


class UserSettings:
    """用户自定义配置."""
    SETTINGS_MODULE = 'UserSettings'

    def __init__(self, default_settings):
        """
        Requests for configuration variables not in this class are satisfied
        from the module specified in default_settings (if possible).
        """
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)

    def __dir__(self):
        return sorted(
            s for s in list(self.__dict__) + dir(self.default_settings)
            if s not in self._deleted
        )

    def is_overridden(self, setting):
        deleted = (setting in self._deleted)
        set_locally = (setting in self.__dict__)
        set_on_default = getattr(self.default_settings, 'is_overridden', lambda s: False)(setting)
        return deleted or set_locally or set_on_default

    def __repr__(self):
        return '<%(cls)s>' % {
            'cls': self.__class__.__name__,
        }
