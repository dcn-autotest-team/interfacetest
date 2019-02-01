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
#       - 2018/7/31 14:16  add by wangxinae
#
# *********************************************************************
"""
+ 模块说明：
    + 概要：
        log模块主要目的是提供一个快捷方便，开箱即用，同时容易扩展显示丰富的日志记录模块。
    + 核心特性：
        1 简单容易使用，无需复杂配置。

        2 使用灵活方便，支持默认格式灵活修改，结合配置文件，实现配置和代码分离。

        3 支持终端颜色显示（目前只在windows下面进行测试通过）
    + 用法：
        使用log的时候会默认给日志设定固定的日志格式，默认格式为：

        `[%(levelname)1.1s %(asctime)s] %(color)s%(message)s%(end_color)s`

        其中(color)和(end_color)为log模块特有表明需要进行颜色显示的内容，其他字段为logging模块所有，详情参见

        https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime

        + log基本用法：

        >>> from library.log import log  # 导入log模块
        >>> log(f'开始记录日志')  # 默认为记录日志等级为Debug
        [D 18年10月26日 09时59分27秒,315毫秒] [<input>:1] 开始记录日志
        >>> log(f'日志信息', level='info')
        [I 18年10月26日 10时00分13秒,447毫秒] [<input>:1] 日志信息
        >>> log(f'日志告警',level='warn')
        [W 18年10月26日 10时00分31秒,623毫秒] [<input>:1] 日志告警
        >>> log(f'日志错误',level='error')
        [E 18年10月26日 10时00分43秒,32毫秒] [<input>:1] 日志错误
        >>> log(f'日志错误',level='critial')
        >>> log('格式化输出', format_print=True)
        [D 18年10月26日 10时34分38秒,148毫秒]
        >>> ####################################################################################################
        >>> # [<input>:1] 格式化输出                                                                           #
        >>> ####################################################################################################
        >>> log('日志文件', log_file='E:/1.log') # 同时支持将日志输出到日志文件中，如果没有1.log会自动创建
        [D 18年10月26日 10时37分42秒,568毫秒] [<input>:1] 日志文件
        >>> log('日志文件', color='blue')  # 串口显示输出内容颜色为蓝色
        [<input>:1] 日志文件
        >>> log('backtrace', color='blue', backtrace=0)  # 关闭backtrace，默认日志开始一级backtrace帮助调试
        backtrace
        >>> log('backtrace', color='blue', backtrace=2)  # 打开上上一级backtrace
        [code.py:91] backtrace
        >>> log('backtrace', color='blue', backtrace=3)
        [code.py:75] backtrace
        >>> import logging
        >>> test_logger = logging.getLogger('test_logger')
        >>> test_logger.addHandler(logging.StreamHandler(sys.stdout))
        >>> log('其他logger',logger=test_logger, level='error')  # 除了使用log模块默认logger之外还可以使用其他logger
        [<input>:1] 其他logger

        + log_instance用法

            提供了一个基于单例模式的日志实例，用户可以在其他项目中导入该实例使用log_instance中的setup方法对日志格式进行
            重新配置和修改，配合ini配置文件能够达到配置与代码分离的目的

        >>> log_instance.logger = log_instance.setup(
        >>> name=const.logger_name,  # 用户从ini获取其他配置文件中读取的数据
        >>> log_file=const.log_file if const.file_log_on else None,  # 用于判断是否生成日志文件
        >>> console_level=const.log_level_in_console, # 用户从ini获取其他配置文件中读取的数据
        >>> fmt=const.log_fmt, # 用户从ini获取其他配置文件中读取的数据
        >>> max_bytes=const.max_bytes_each, # 用户从ini获取其他配置文件中读取的数据
        >>> backup_count=const.backup_count, # 用户从ini获取其他配置文件中读取的数据
        >>> logfile_level=const.log_level_in_logfile, # 用户从ini获取其他配置文件中读取的数据
        >>> display_to_console=const.console_log_on, # 用户从ini获取其他配置文件中读取的数据
        >>> )

"""
import functools
import logging
import logging.handlers
import os
import sys
import threading
from logging.handlers import RotatingFileHandler, SysLogHandler
from pprint import pformat

from colorama import Fore, init

from library.conf import settings as const
from library.decorator import SingletonMeta

__all__ = ['log', 'log_instance', 'log_function_call']

# init(autoreset=True)  # 初始化colorama，用于支持颜色显示和设置
sys.stderr = sys.stdout  # 未配置root logger时候日志级别为 warning, 输入到stderr， 默认日志pycharm中默认设置stderr显示是红色字体


def _remove_internal_loggers(logger_to_update, display_to_console=False):
    """
    从指定的logger移除内部的handler (例如 stderr logger and file logger)

    :param logger_to_update: 要移除的logger
    :param display_to_console: 默认不输出到串口
    """
    for handler in list(logger_to_update.handlers):
        if hasattr(handler, const.INTERNAL_LOGGER_ATTR):
            if isinstance(handler, RotatingFileHandler):
                logger_to_update.removeHandler(handler)
            elif isinstance(handler, SysLogHandler):
                logger_to_update.removeHandler(handler)
            elif isinstance(handler, logging.StreamHandler) and (not display_to_console):
                logger_to_update.removeHandler(handler)


def _line(back=0):
    # noinspection PyProtectedMember
    return sys._getframe(back + 1).f_lineno


def _file(back=0):
    # noinspection PyProtectedMember
    return os.path.basename(sys._getframe(back + 1).f_code.co_filename)


def _pid():
    # noinspection PyProtectedMember
    return str(os.getpid()) + ':' + str(threading.current_thread().ident)


# -----------------------------------------------------------------------------------------------------------


def safe_unicode(s):
    """
    将bytes, unicode, or None安全的转换成unicode
    :param s:等待装换的值
    :return: unicode

    >>> safe_unicode('123')
    '123'
    >>> safe_unicode(b'123')
    '123'
    >>> safe_unicode('中国')
    '中国'
    >>> safe_unicode('@！@#F%')
    '@！@#F%'
    >>> safe_unicode('0x1b')
    '0x1b'
    >>> safe_unicode('0x1b1c')
    '0x1b1c'
    >>> safe_unicode('0x1b1cT占用')
    '0x1b1cT占用'

    """

    def to_unicode(value):
        """
        string装换成unicode
        """
        if isinstance(value, (str, type(None))):
            return value
        if not isinstance(value, bytes):
            raise TypeError(
                "Expected bytes, unicode, or None; got %r" % type(value))
        return value.decode("utf-8")

    try:
        return to_unicode(s)
    except UnicodeDecodeError:
        return repr(s)


class LogFormatter(logging.Formatter):
    """
    自定义log formatter
    支持日志颜色化输出,默认开启，如果日志输出对象为file，则关闭color输出
    支持unicode编码(乱码或者异常码都支持)
    """

    def __init__(self,
                 color=True,
                 fmt=const.DEFAULT_FORMAT,
                 date_fmt=const.DEFAULT_DATE_FORMAT,
                 colors=const.LOGLEVEL_COLOR_OPTS):

        logging.Formatter.__init__(self, datefmt=date_fmt)

        self._fmt = fmt
        self._colors = {}
        self._normal = ''

        if color:
            self._colors = colors
            self._normal = Fore.RESET

    def formatTime(self, record, date_fmt=None):
        """
        重载日期格式化,支持中文格式显示，以及毫秒显示
        """
        import time
        ct = self.converter(record.created)
        if date_fmt:
            try:
                fmt_time = time.strftime(date_fmt, ct)
            except UnicodeEncodeError:  # python3.4/5/6版本中对中文字符进行strftime会出现UnicodeEncodeError，处理此处异常
                # bug号为https: // bugs.python.org / issue8304
                fmt_time = time.strftime(date_fmt.encode('unicode-escape').decode(), ct)
                fmt_time = fmt_time.encode().decode('unicode-escape')
            return f'{fmt_time},{record.msecs:.0f}毫秒'
        else:
            return f'{time.strftime(self.default_time_format, ct)},{record.msecs:.0f}毫秒'

    def format(self, record):

        try:
            message = record.getMessage()
            assert isinstance(message, str)
            # noinspection PyTypeChecker
            record.message = safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(
                safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")


class Log(metaclass=SingletonMeta):
    def __init__(self):
        self._loglevel = logging.DEBUG  # 全局log level
        self._logfile = None
        self._formatter = None
        self.logger = self.setup()

    def reset(self):
        """setup()不传入参数就是reset"""
        self.logger = self.setup()

    def setup(self, name=None, log_file=None, console_level=logging.DEBUG, fmt=None, max_bytes=0, backup_count=0,
              logfile_level=logging.DEBUG, display_to_console=True):
        """
        日志设置基础函数
        如果要设置的日志name已经存在，使用旧的日志实例，如果没有重新创建
        如果指定了log_file会创建RotatingFile文件，如果配置max_bytes/backup_count！=0, 日志将进行翻滚

        :param name: 日志logger名称
        :param log_file: 指定要创建日志文件路径,如果指定日志路径不存在，默认行为创建
        :param console_level: Stream Handler日志级别
        :param fmt: Logging.Formatter对象,默认为LogFormatter实例
        :param max_bytes: 最大文件存储大小
        :param backup_count: 翻滚文件个数
        :param logfile_level: RotatingFile Handler日志级别
        :param display_to_console:是否打印到Console
        :return:logger
        """
        _logger = logging.getLogger(name or __name__)  # 如果
        _logger.propagate = False  # 禁止propagate到handler
        _effective_level = min(logfile_level, console_level)
        _logger.setLevel(_effective_level)  # 设置全局默认有效日志级别
        log_file_fmt = None
        if fmt and isinstance(fmt, str):
            if log_file:
                log_file_fmt = LogFormatter(fmt=fmt, color=False)  # 防止颜色打印到file中
            fmt = LogFormatter(fmt=fmt)
            self._formatter = fmt
        # 处理新生成的logger,需要判断通过name或者_name__生成的logger是否被使用过
        stderr_stream_handler = None
        for handler in list(_logger.handlers):
            if hasattr(handler, const.INTERNAL_LOGGER_ATTR):
                if isinstance(handler, logging.FileHandler):
                    # 内部的FileHandler需要被移除，这样重新setup的时候能够重新设置一个log文件
                    _logger.removeHandler(handler)
                    continue
                elif isinstance(handler, logging.StreamHandler):
                    stderr_stream_handler = handler

            # 重新设置日志handler的level 和 format
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(logfile_level)
            elif isinstance(handler, logging.StreamHandler):
                handler.setLevel(console_level)
            else:
                handler.setLevel(logfile_level)
            handler.setFormatter(fmt or LogFormatter())

        if display_to_console:
            if stderr_stream_handler is None:
                stderr_stream_handler = logging.StreamHandler()
                setattr(stderr_stream_handler, const.INTERNAL_LOGGER_ATTR, True)
                stderr_stream_handler.setLevel(console_level)
                stderr_stream_handler.setFormatter(fmt or LogFormatter())
                # ===============================================================================================
                # 依据console_level级别输出指定内容，例如console_level=logging.INFO 那么logger.debug('123')将不会输出
                # type('UserFilter', (logging.Filter,),{'filter': staticmethod(lambda r: r.levelno >= console_level)})
                # type(name, bases, dict) -> 返回一个类
                # name为要生成的类名，bases为继承的基类，dict为新生成的类的__dict__
                # class UserFilter(logging.Filter):
                #     @staticmethod-->此处用静态方法的目的是为了去self化，以便于可以通过class传入
                #     def filter(record):
                #         """ Determine if the specified record is to be logged. if True emit msg"""
                #         return True if record.levelno >= console_level else False
                # ===============================================================================================
                stderr_stream_handler.addFilter(type('', (logging.Filter,),
                                                     {'filter': staticmethod(lambda r: r.levelno >= console_level)}))
                _logger.addHandler(stderr_stream_handler)
        else:
            # 如果日志不输出到console，去掉对应日志handler
            if stderr_stream_handler is not None:
                _logger.removeHandler(stderr_stream_handler)

        if log_file:
            from library.file import ensure_dir
            ensure_dir(log_file)
            rotating_file_handler = RotatingFileHandler(filename=log_file, maxBytes=max_bytes, backupCount=backup_count,
                                                        encoding='utf-8')
            setattr(rotating_file_handler, const.INTERNAL_LOGGER_ATTR, True)
            rotating_file_handler.setLevel(logfile_level or console_level)
            rotating_file_handler.setFormatter(log_file_fmt or LogFormatter(color=False))
            # 依据logfile_level级别输出指定内容，例如logfile_level=logging.INFO 那么logger.debug('123')将不会输出
            rotating_file_handler.addFilter(type('', (logging.Filter,),
                                                 {'filter': staticmethod(lambda r: r.levelno >= logfile_level)}))
            _logger.addHandler(rotating_file_handler)
            self._logfile = log_file
        self._loglevel = _logger.getEffectiveLevel()
        logging.root = _logger
        return _logger

    def formatter(self, fmt, force=False):
        """
        对默认logger的默认handler(logger中含有INTERNAL_LOGGER_ATTR属性的为True的handler)设置formatter
        ，如果对logger增加了addHandler A的操作之后，formatter函数中的fmt参数不会作用于A，除非force=True才会生效

        :param fmt: format
        :param force: 强制使用用户自定义
        :return: None
        """
        for handler in list(self.logger.handlers):
            if hasattr(handler, const.INTERNAL_LOGGER_ATTR) or force:
                handler.setFormatter(fmt)
        self._formatter = fmt

    def loglevel(self, level=logging.DEBUG, force=False):
        """
        对默认logger的默认handler(logger中含有INTERNAL_LOGGER_ATTR属性的为True的handler)设置loglevel
        ，如果对logger增加了addHandler A的操作之后，loglevel函数中的level不会作用于A，除非force=True才会生效
        """
        self.logger.setLevel(level)  # 设置logger的level
        # 设置handler中的level
        for handler in list(self.logger.handlers):
            if hasattr(handler, const.INTERNAL_LOGGER_ATTR) or force:
                # 如果默认logger通过logfile函数设置过loglevel，此时logfile中的level优先级要高于loglevel函数优先级，因此跳过
                if hasattr(handler, const.INTERNAL_CUSTOM_LOGLEVEL):
                    continue
                handler.setLevel(level)
        self._loglevel = level

    def logfile(self, filename, fmt=None, mode='a', max_bytes=0, backup_count=0, encoding=None, log_level=None,
                display_to_console=True):
        """
        设置默认logger支持文件格式保存，

        :param display_to_console:
        :param filename: 日志文件
        :param fmt: 格式 优先级 fmt > _formatter(当前默认formatter) >　LogFormatter（为空依次向后取值）
        :param mode: 日志文件模式
        :param max_bytes: 触发日志翻滚的最大字节
        :param backup_count: 翻滚日志数量上限
        :param encoding: 日志编码
        :param log_level: 日志默认级别 优先级log_level > _loglevel
        :return: None
        """
        # 如果内部RotatingFileHandler存在则移除
        _remove_internal_loggers(self.logger, display_to_console)
        if filename:
            rotating_file_handler = RotatingFileHandler(filename, mode=mode, maxBytes=max_bytes,
                                                        backupCount=backup_count,
                                                        encoding=encoding or 'utf-8')

            # Set internal attributes on this handler
            setattr(rotating_file_handler, const.INTERNAL_LOGGER_ATTR, True)
            if log_level:
                setattr(rotating_file_handler, const.INTERNAL_CUSTOM_LOGLEVEL, True)

            # Configure the handler and add it to the logger
            rotating_file_handler.setLevel(log_level or self._loglevel)
            rotating_file_handler.setFormatter(fmt or self._formatter or LogFormatter(color=False))
            self.logger.addHandler(rotating_file_handler)
            self._logfile = filename

    # 关联默认logger的函数
    def syslog(self, logger_to_update=None, facility=SysLogHandler.LOG_USER, display_to_console=False):
        """
        设置系统日志

        :param logger_to_update: 用于syslog的logger
        :param facility: syslog facility
        :param display_to_console: 默认不输出到串口
        :return 新SysLogHandler
        """
        # 移除内部logger
        _remove_internal_loggers(logger_to_update or self.logger, display_to_console)

        # 设置 syslog handler指定的facility
        syslog_handler = SysLogHandler(facility=facility)
        setattr(syslog_handler, const.INTERNAL_LOGGER_ATTR, True)
        logger_to_update.addHandler(syslog_handler)
        return syslog_handler


log_instance = Log()


def log_function_call(func):
    """调试函数"""

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join(["%s=%s" % (key, kwargs[key]) for key in kwargs])
        if args_str and kwargs_str:
            all_args_str = ", ".join([args_str, kwargs_str])
        else:
            all_args_str = args_str or kwargs_str
        log_instance.logger.debug("%s(%s)", func.__name__, all_args_str)
        return func(*args, **kwargs)

    return wrap


def log(*msg, level='debug', format_print=False, log_file=None, logger=None, backtrace=1, pprint=True, color=None):
    """
    + 说明：
        生成指定级别的日志便捷函数

    :param color: 通过设置颜色指定显示文字的颜色（大小写均可），但是不带日志格式化前缀
                  color可选范围如下

                  {
                  'BLACK', 'BLUE', 'CYAN', 'GREEN',
                  'LIGHTBLACK_EX', 'LIGHTBLUE_EX', 'LIGHTCYAN_EX',
                  'LIGHTGREEN_EX', 'LIGHTMAGENTA_EX', 'LIGHTRED_EX',
                  'LIGHTWHITE_EX', 'LIGHTYELLOW_EX', 'MAGENTA',
                  'RED', 'RESET', 'WHITE', 'YELLOW'
                  }
    :param pprint: pretty print 开启pprint格式化
    :param backtrace: backtrace=1显示代码中调用log函数的模块名加代码中行数[suite.py:216]，其他依次回溯backtrace
    :param format_print: 是否格式化输出
    :param logger: logger对象，如果为空为默认log_instance
    :param log_file: 根据log_file生成新的log日志（输入:'test.log'则会在logs文件夹下面生成对应log，
                     如果输入‘E:/test/test.log’则在对应目录下面生成log，如果路径中的文件夹不存在，自动创建）
                     TODO:后续要根据log等级在串口输出不同颜色的log
    :param msg: 日志信息
    :param level: 日志等级
    :return: None
    """
    _level = getattr(logging, str(level).upper(), None) if level else None  # level不为None的时候判断日志级是否为合法日志级别

    if _level is None:
        raise (ValueError, '日志级别非法或者为空')

    if log_file:
        log_instance.logfile(log_file)

    for _msg in msg:
        from .utils import print_format
        from collections.abc import Mapping
        if pprint and isinstance(_msg, Mapping):  # 只格式化Mapping类型的数据即可({})
            _msg = pformat(_msg, width=60)
            _msg = f"\n{'='*8}pretty message{'='*8}\n{_msg}\n{'='*30}"

        if backtrace:  # 打印 backtrace
            _msg = f'[{_file(backtrace)}:{_line(backtrace)}] {_msg}'

        logger = logger if logger else log_instance.logger
        _msg = print_format(_msg) if format_print else str(_msg)
        if color:
            for handler in list(logger.handlers):
                if hasattr(handler, const.INTERNAL_LOGGER_ATTR):
                    if isinstance(handler, logging.FileHandler):
                        # 内部的FileHandler不能有颜色color,此处为hack直接从stream中写入，不带[D 18年10月18日 16时38分24秒,978毫秒]
                        handler.stream.write(_msg + '\n')
                    elif isinstance(handler, logging.StreamHandler):
                        __msg = f"{getattr(Fore, color.upper(), '')}{_msg}{Fore.RESET}"
                        handler.stream.write(__msg + '\n')
        else:
            getattr(logger, str(level).lower())(_msg)
