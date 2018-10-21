#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# lazy.py -
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
#       - 2018/9/22 10:39  add by yanwh
#
# *********************************************************************
import operator


class _MissingObject(object):
    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'


_missing = _MissingObject()


# noinspection PyArgumentList
class LazyProperty(property):
    def __init__(self, name=None, doc=None, readable=True, settable=False, **kwargs):
        """
        :param name: 用户自定义访问和设置的属性名称
        :param doc: 被装饰的函数的doc或者指定doc
        :param readable: 设置被装饰属性是否可读
        :param settable: 设置被装饰的属性是否可写
        """
        self.__name__ = name
        self.__doc__ = doc
        self.settable = settable
        self.readable = readable
        super(LazyProperty, self).__init__(kwargs.get('fget', None), kwargs.get('fset', None),
                                           kwargs.get('fdel', None), kwargs.get('doc', None))

    def __call__(self, method=None, **kwargs):
        """
        :param method: 被装饰的类方法名称
        :param kwargs: 指定fget和fset fdel doc，跟property保持一致
        :return: self
        """
        self.__name__ = self.__name__ or (method.__name__ if callable(method) else None)
        self.__doc__ = self.__doc__ or (method.__doc__ if callable(method) else None)
        self.__module__ = method.__module__ if callable(method) else None
        self.method = method

        return self  # 后面调用getter和setter使用

    def __get__(self, *args, **kwargs):  # 本来应该撰写成def __get__(self, instance, owner)为了通过pycharm检查才写成这样
        """
        :param args: 为了或者被装饰类的实例instance
        :param kwargs: None
        :return: 要访问的属性值
        """

        def _parse_vars(var):
            return var[0], var[1]

        instance, cls = _parse_vars(args)
        if instance is None:
            return self
        result = instance.__dict__.get(self.__name__, _missing)  # 属性缓存
        if result is _missing:
            if self.fget:
                result = self.fget(instance)
            else:
                if self.readable:
                    result = self.method(instance)
                else:
                    raise AttributeError('can\'t get attribute')
            instance.__dict__[self.__name__] = result
        return result

    def __set__(self, instance, value: 'value to set'):
        """
        :param instance: 被装饰的类的instance
        :param value: 要设置的值
        :return: None
        """
        if instance is None:
            raise AttributeError
        if self.fset:
            self.fset(instance, value)
        else:
            if self.settable:
                instance.__dict__[self.__name__] = value
            else:
                raise AttributeError('can\'t set attribute')

    def setter(self, fset):
        """
        同property
        :param fset: fset函数
        :return: self
        """
        return type(self)(name=self.__name__, doc=self.__doc__, readable=self.readable, settable=self.settable,
                          fget=self.fget, fset=fset, fdel=self.fdel)(method=self.method)

    def getter(self, fget):
        """
        同property
        :param fget: fget函数
        :return: self
        """
        return type(self)(name=self.__name__, doc=self.__doc__, readable=self.readable, settable=self.settable
                          , fget=fget, fset=self.fset, fdel=self.fdel)(method=self.method)


lazy_property = LazyProperty


class _TestLazyProperty:
    """
    >>> tlp=_TestLazyProperty(123)
    >>> tlp.a
    123
    >>> tlp.a=1
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "<input>", line 79, in __set__
    AttributeError: can't set attribute
    >>> tlp.aa = 110
    >>> tlp.a
    123
    >>> tlp.aa
    123
    >>> tlp.a=111
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "<input>", line 79, in __set__
    AttributeError: can't set attribute
    >>> tlp.__dict__
    {'_x': 110, '_y': 123}
    >>> tlp.b
    110
    >>> tlp.b=111
    >>> tlp.b
    111
    >>> tlp.c
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "<input>", line 61, in __get__
    AttributeError: can't get attribute
    >>> tlp.cc
    220
    >>> tlp.xx
    110
    >>> tlp.xx=1
    >>> tlp.xx
    1
    >>> tlp.__dict__
    {'_x': 1, '_y': 123, 'b': 111, 'c': 220}
    """

    def __init__(self, x):
        self._x = x

    @lazy_property(name='_y')
    def a(self):
        return self._x

    @a.setter
    def aa(self, value):
        self._x = value

    @lazy_property(settable=True)
    def b(self):
        return self._x

    @lazy_property(readable=False)
    def c(self):
        return self._x

    @c.getter
    def cc(self):
        return self._x * 2

    def d(self):
        return self._x

    def e(self, value):
        self._x = value

    xx = lazy_property(name='_x', fget=d, fset=e, fdel=lambda self: None, doc=None)


empty = object()


def new_method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)

    return inner


class LazyObject(object):
    """
    用于继承与它的子类可以延迟进行初始化，从而用于改变子类的行为
    """

    _wrapped = None
    _kwargs = None

    def __init__(self):
        self._wrapped = empty

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self, name, value):
        if name in ["_wrapped", "_kwargs"]:
            self.__dict__[name] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        子类必须要实现该方法
        """
        raise NotImplementedError(
            'LazyObject 必须要提供一个 _setup() 方法'
        )

    def __getstate__(self):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__dict__

    @classmethod
    def __newobj__(cls, *args):
        return cls.__new__(cls, *args)

    def __reduce_ex__(self, proto):
        if proto >= 2:
            return self.__newobj__, (self.__class__,), self.__getstate__()

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            result = type(self)()
            memo[id(self)] = result
            return result
        from copy import deepcopy
        return deepcopy(self._wrapped, memo)

    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)

    __dir__ = new_method_proxy(dir)

    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)

    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)
