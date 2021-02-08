# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import xlrd
import re
import Repository


def hyperlink_statistics(src_path, dst_path):
    r_sheet = xlrd.open_workbook(src_path).sheet_by_index(0)
    count_dict = {}
    for rowx in range(0, r_sheet.nrows):
        for colx in range(0, r_sheet.row_len(rowx)):
            match = re.search(r'https?://[^/]*', r_sheet.cell_value(rowx, colx), re.I)
            if match:
                Repository.update_count_dict(count_dict, [match.group()])
    Repository.init_workbook(dst_path, ['Hyperlink', 'Count'])
    Repository.write_workbook_key_value(dst_path, count_dict, 1)


if __name__ == '__main__':
    hyperlink_statistics(r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Achievement\Linux Kernel CVE Info.xls',
                         r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Achievement\Linux Kernel Reference Hyperlink Count.xls')
