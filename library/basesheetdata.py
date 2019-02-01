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
#       - 2018/7/25 16:40  add by wangxinae
#
# *********************************************************************


class OperationExcel:
    """Operate Excel"""
    def __init__(self, file_name, sheet_name):
        """
        + 说明：
            根据输入的excel和sheet名称来找到所需要测试的文件，提供了文件内容读取的方法。

        :param file_name: 测试使用的excel文件名称
        :param sheet_name: 测试使用的excel文件中的sheet名称
        """
        self.file_name = file_name
        self.sheet_name = sheet_name

    @property
    def get_sheet(self):
        """
        :return: 获取到excel中sheet内容
        """
        import xlrd  # 延迟导入，防止循环导入
        data = xlrd.open_workbook(self.file_name)
        sheet = data.sheet_by_name(self.sheet_name)
        return sheet

    @property
    def get_rows(self):
        """
        :return: 获取sheet表数
        """
        rows = self.get_sheet.nrows
        return rows

    @property
    def get_col(self):
        """
        :return: 获取sheet表列数
        """
        cols = self.get_sheet.ncols
        return cols

    @property
    def get_seq(self):
        """
        :return: 获取sheet表中每行的测试用例编号
        """
        seqs = []
        for i in range(1, self.get_rows):
            seqs.append(self.get_sheet.cell_value(i, 0))
        return seqs

    @property
    def get_name(self):
        """
        :return: 获取sheet表中每行的测试用例名称
        """
        tn = []
        for i in range(1, self.get_rows):
            tn.append(self.get_sheet.cell_value(i, 1))
        return tn

    @property
    def get_precondition(self):
        """
        :return: 获取sheet表中每行测试的预制条件
        """
        pre_condition = []
        for i in range(1, self.get_rows):
            pre_condition.append(self.get_sheet.cell_value(i, 2))
        return pre_condition

    @property
    def get_url(self):
        """
        :return: 获取sheet表中每行测试的url
        """
        url = []
        for i in range(1, self.get_rows):
            url.append(self.get_sheet.cell_value(i, 3))
        return url

    @property
    def get_date(self):
        """
        :return: 获取sheet表中每行测试的输入数据
        """
        data = []
        for i in range(1, self.get_rows):
            data.append(self.get_sheet.cell_value(i, 4))
        return data

    @property
    def get_method(self):
        """
        :return: 获取sheet表中每行的测试方法
        """
        method = []
        for i in range(1, self.get_rows):
            method.append(self.get_sheet.cell_value(i, 5))
        return method

    @property
    def get_status_code(self):  # need fix
        """
        :return: 获取sheet表中每行的响应参数
        """
        status_code = []
        for i in range(1, self.get_rows):
            status_code.append(self.get_sheet.cell_value(i, 6))
        return status_code

    get_statuscode = get_status_code

    @property
    def get_code(self):
        """
        :return: 获取sheet表中每行的响应检查点
        """
        code = []
        for i in range(1, self.get_rows):
            code.append(self.get_sheet.cell_value(i, 7))
        return code

    @property
    def get_error_code(self):
        """
        :return: 获取sheet表中每行的错误检查点
        """
        error_code = []
        for i in range(1, self.get_rows):
            error_code.append(self.get_sheet.cell_value(i, 8))
        return error_code

    sheets = get_sheet
    error_codes = get_error_code
    codes = get_code
    status_codes = get_status_code
    methods = get_method
    data = get_date
    urls = get_url
    preconditions = get_precondition
    names = get_name
    seqs = get_seq
    rows = get_rows
    cols = get_col

OperateExcel = OperationExcel
