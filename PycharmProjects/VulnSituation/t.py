# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import xlrd
import re
import Repository


def get_info_dict(r_sheet, row_index):
    info_dict = {}
    info_dict.update({'CVE ID': str(r_sheet.cell(row_index, 0).value).strip()})
    info_dict.update({'Year': re.match(r'CVE-(\d+)-\d+', info_dict['CVE ID'], re.I).group(1)})
    info_dict.update({'Interval': int(r_sheet.cell(row_index, 4).value)})
    match = re.search(r'\(CWE-(\w+)\)', str(r_sheet.cell(row_index, 5).value).strip(), re.I)
    info_dict.update({'CWE ID': -1 if not match else match.group(1)})
    info_dict.update({'Level': Repository.get_dict_value(
        {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3},
        str(r_sheet.cell(row_index, 6).value).strip().split(';')[1])}
    )
    info_dict.update({'Score': float(str(r_sheet.cell(row_index, 6).value).strip().split(';')[0])})
    info_dict.update({'Attack Vector': Repository.get_dict_value(
        {'Local': 1, 'Adjacent Network': 2, 'Network': 3},
        str(r_sheet.cell(row_index, 7).value).strip())}
    )
    info_dict.update({'Access Complexity': Repository.get_dict_value(
        {'Low': 1, 'Medium': 2, 'High': 3},
        str(r_sheet.cell(row_index, 8).value).strip())}
    )
    info_dict.update({'Authentication': Repository.get_dict_value(
        {'None': 1, 'Single': 2, 'Multiple': 3},
        str(r_sheet.cell(row_index, 9).value).strip())}
    )
    info_dict.update({'Confidentiality Impact': Repository.get_dict_value(
        {'None': 1, 'Partial': 2, 'Complete': 3},
        str(r_sheet.cell(row_index, 10).value).strip())}
    )
    info_dict.update({'Integrity Impact': Repository.get_dict_value(
        {'None': 1, 'Partial': 2, 'Complete': 3},
        str(r_sheet.cell(row_index, 11).value).strip())}
    )
    info_dict.update({'Availability Impact': Repository.get_dict_value(
        {'None': 1, 'Partial': 2, 'Complete': 3},
        str(r_sheet.cell(row_index, 12).value).strip())}
    )
    return info_dict


def character_factor_digitization(src_path, dst_path):
    r_workbook = xlrd.open_workbook(src_path)
    r_sheet = r_workbook.sheet_by_index(0)
    Repository.init_workbook(dst_path,
                             ['CVE ID', 'Year', 'Interval', 'CWE ID', 'Level'])
    for row_index in range(2, r_sheet.nrows):
        print('\rRow Index:' + str(row_index - 1), end='')
        info_dict = get_info_dict(r_sheet, row_index)
        Repository.write_workbook(dst_path, info_dict, row_index - 1)


if __name__ == '__main__':
    character_factor_digitization(
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Linux Kernel Character Factor(Middle).xls',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Linux Kernel Character Factor(Middle)(Digit).xls'
    )
