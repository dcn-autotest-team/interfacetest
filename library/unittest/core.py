#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# core.py - 
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
#       - 2018/9/30 17:30  add by yanwh
#
# *********************************************************************
import datetime
import io
import json
import os
import shutil
import sys
import time
import unittest
from xml.sax import saxutils

from library.conf import settings as const
from .template import Template_mixin
from ..log import log

result_data = dict()
result_data['testResult'] = []
current_class_name = ""


class OutputRedirect(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirect = OutputRedirect(sys.stdout)
stderr_redirect = OutputRedirect(sys.stderr)


class _TestResult(unittest.TestResult):
    def __init__(self, verbosity=1):
        super().__init__(verbosity)
        self.outputBuffer = io.StringIO()
        self.raw_stdout = None
        self.raw_stderr = None
        self.success_count = 0
        self.failure_count = 0
        self.skip_count = 0
        self.error_count = 0
        self.verbosity = verbosity
        self.result = []
        self._case_start_time = 0
        self._case_run_time = 0

    def startTest(self, test):
        self._case_start_time = time.time()
        super().startTest(test)
        stdout_redirect.fp = self.outputBuffer
        stderr_redirect.fp = self.outputBuffer
        self.raw_stdout = sys.stdout
        self.raw_stderr = sys.stderr
        sys.stdout = stdout_redirect
        sys.stderr = stderr_redirect

    def complete_output(self):
        self._case_run_time = time.time() - self._case_start_time
        if self.raw_stdout:
            sys.stdout = self.raw_stdout
            sys.stderr = self.raw_stderr
            self.raw_stdout = None
            self.raw_stderr = None
        result = self.outputBuffer.getvalue()
        self.outputBuffer.seek(0)
        self.outputBuffer.truncate()
        return result

    def stopTest(self, test):
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        super().addSuccess(test)
        output = self.complete_output()
        self.result.append((0, test, output, '', self._case_run_time))

    # noinspection PyProtectedMember
    def addError(self, test, err):
        self.error_count += 1
        super().addError(test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str, self._case_run_time))
        log(f"执行测试用例 {test._testMethodName if hasattr(test, '_testMethodName') else ''} 遇到错误", level='error')
        if const.SHOW_ERROR_TRACEBACK:
            log(_exc_str, level='error')

    def addSkip(self, test, reason):
        self.skip_count += 1
        super().addSkip(test, reason)
        self.result.append((3, test, "", "", 0.0))

    # noinspection PyProtectedMember
    def addFailure(self, test, err):
        self.failure_count += 1
        super().addFailure(test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str, self._case_run_time))
        log(f'执行测试用例 {test._testMethodName} 失败 ', level='error')
        if const.SHOW_ERROR_TRACEBACK:
            log(_exc_str, level='error')


class CoreTestRunner(Template_mixin):
    def __init__(self, report_title, report_file, stream=None, verbosity=1, description=""):
        self.report_file = report_file
        self.verbosity = verbosity
        self.title = report_title
        self.stream = stream
        self.description = description
        self.start_time = datetime.datetime.now()
        self.stop_time = None

    def run(self, test):
        # log(f'\n=======================项目初始化参数====================\n{const.format()}')
        log("开始进行测试", level='info')

        result = _TestResult(self.verbosity)
        test(result)
        self.stop_time = datetime.datetime.now()
        self.generate_report(result)
        log('Time Elapsed: {}'.format(self.stop_time - self.start_time), level='info')

        if const.CREATE_ZTEST_STYLE_REPORT:
            file = self.report_file
            shutil.copy2(os.path.join(os.path.dirname(__file__), "template.html"), file)
            with open(file, "r+", encoding='utf-8') as f:
                content = f.read().replace(r"${resultData}", json.dumps(result_data, ensure_ascii=False, indent=4))
                f.seek(0)
                f.write(content)

    @staticmethod
    def sort_result(case_results):
        rmap = {}
        classes = []
        for n, t, o, e, run_time in case_results:
            cls = t.__class__
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e, run_time))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    def get_report_attributes(self, result):
        start_time = str(self.start_time)[:19]
        duration = str(self.stop_time - self.start_time)
        status = []
        if result.success_count:
            status.append('<span class="text text-success">Pass <strong>%s</strong></span>' % result.success_count)
        if result.failure_count:
            status.append('<span class="text text-danger">Failure <strong>%s</strong></span>' % result.failure_count)
        if result.error_count:
            status.append('<span class="text text-warning">Error <strong>%s</strong></span>' % result.error_count)
        if result.skip_count:
            status.append('<span class="text text-info">Skip <strong>%s</strong></span>' % result.skip_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'

        result_data["testName"] = self.title
        result_data["beginTime"] = start_time
        result_data["totalTime"] = duration
        return [
            ('Start Time', start_time),
            ('Duration', duration),
            ('Status', status),
        ]

    def generate_report(self, result):
        report_attrs = self.get_report_attributes(result)
        generator = 'BSTestRunner'
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        output = self.HTML_TMPL % dict(
            title=self.title,
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report)
        if const.CREATE_BSTEST_STYLE_REPORT:
            if self.stream:
                self.stream.write(output.encode('utf8'))
            elif self.report_file:
                file = self.report_file
                with open(file, "wb") as f:
                    f.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=name,
                value=value,
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
        )
        return heading

    def _generate_report(self, result):
        rows = []
        sorted_result = self.sort_result(result.result)
        for cid, (cls, cls_results) in enumerate(sorted_result):
            pass_num = fail_num = error_num = skip_num = 0
            for case_state, *_ in cls_results:
                if case_state == 0:
                    pass_num += 1
                elif case_state == 1:
                    fail_num += 1
                elif case_state == 2:
                    error_num += 1
                else:
                    skip_num += 1

            name = "{}.{}".format(cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name
            global current_class_name
            current_class_name = name

            row = self.REPORT_CLASS_TMPL % dict(
                style=error_num > 0 and 'text text-warning' or fail_num > 0 and 'text text-danger' or 'text '
                                                                                                      'text-success',
                desc=desc,
                count=pass_num + fail_num + error_num + skip_num,
                Pass=pass_num,
                fail=fail_num,
                error=error_num,
                skip=skip_num,
                cid='c%s' % (cid + 1),
            )
            rows.append(row)

            for tid, (case_state, t, o, e, run_time) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, case_state, t, o, e, run_time)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count + result.skip_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            skip=str(result.skip_count),
        )

        result_data["testPass"] = result.success_count
        result_data["testAll"] = result.success_count + result.failure_count + result.error_count + result.skip_count
        result_data["testFail"] = result.failure_count
        result_data["testSkip"] = result.skip_count

        return report

    def _generate_report_test(self, rows, class_id, case_id, n, t, o, e, run_time):
        has_output = bool(o or e)
        if n == 0:
            case_tr_id = "pt{}.{}".format(class_id + 1, case_id + 1)
        elif n == 1:
            case_tr_id = "ft{}.{}".format(class_id + 1, case_id + 1)
        elif n == 2:
            case_tr_id = "ft{}.{}".format(class_id + 1, case_id + 1)
        elif n == 3:
            case_tr_id = "st{}.{}".format(class_id + 1, case_id + 1)
        else:
            case_tr_id = ""
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        tmpl_pass = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL_PASS or self.REPORT_TEST_NO_OUTPUT_TMPL
        tmpl_fail = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL_FAIL or self.REPORT_TEST_NO_OUTPUT_TMPL

        ouptut = self.REPORT_TEST_OUTPUT_TMPL % dict(
            output=saxutils.escape(o + e),
        )

        case_data = {}
        global current_class_name
        case_data['className'] = current_class_name
        case_data['methodName'] = name
        case_data['spendTime'] = "{:.2}S".format(run_time)
        case_data['description'] = doc
        case_data['log'] = o + e
        if self.STATUS[n] == "Pass":
            case_data['status'] = "成功"
        if self.STATUS[n] == "Fail":
            case_data['status'] = "失败"
        if self.STATUS[n] == "Error":
            case_data['status'] = "错误"
        if self.STATUS[n] == "Skip":
            case_data['status'] = "跳过"
        result_data['testResult'].append(case_data)

        if self.STATUS[n] == "Pass":
            row = tmpl_pass % dict(
                tid=case_tr_id,
                Class=(n == 0 and 'hiddenRow' or 'text text-success'),
                style=n == 2 and 'text text-warning' or (n == 1 and 'text text-danger' or 'text text-success'),
                desc=desc,
                script=ouptut,
                status=self.STATUS[n],
            )
        else:
            row = tmpl_fail % dict(
                tid=case_tr_id,
                Class=(n == 0 and 'hiddenRow' or 'text text-success'),
                style=n == 2 and 'text text-warning' or (n == 1 and 'text text-danger' or 'text text-success'),
                desc=desc,
                script=ouptut,
                status=self.STATUS[n],
            )

        rows.append(row)
