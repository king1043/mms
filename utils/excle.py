# -*- coding: utf-8 -*-
'''
Created on 2018-04-23 14:25
---------
@summary:
---------
@author: Boris
'''

import xlrd

class Excle():
    def __init__(self, file):
        self._excle = xlrd.open_workbook(file)

    def get_sheet_names(self):
        return workbook.sheet_names()

    def get_rows(self, sheet_name, row_id):
        '''
        @summary:
        ---------
        @param sheet_name:
        @param row_id: 0开始
        ---------
        @result:
        '''

　　    sheet2 = workbook.sheet_by_name(sheet_name)
        return sheet2.row_values(row_id)

    def get_cols(self, sheet_name, col_id):
        '''
        @summary:
        ---------
        @param sheet_name:
        @param col_id:0开始
        ---------
        @result:
        '''

　　    sheet2 = workbook.sheet_by_name(sheet_name)

　　    return sheet2.col_values(col_id)

if __name__ == '__main__':
    excle = Excle('../')