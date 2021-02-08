# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import xlrd
import re
import Repository


def get_info_dict(r_sheet, rowx, all_cwe_id_list):
    info_dict = {}

    info_dict.update({'Interval': int(r_sheet.cell(rowx, 4).value)})
    for cwe_id in all_cwe_id_list:
        info_dict.update({cwe_id: 0})
    match = re.search(r'\(([^()]*)\)$', str(r_sheet.cell(rowx, 5).value).strip(), re.I)
    info_dict.update({match.group(1): 1})

    info_dict.update(
        {
            'Score':
                Repository.normalization(
                    float(str(r_sheet.cell(rowx, 6).value).strip().split(';')[0]),
                    0,
                    10
                )
        }
    )
    info_dict.update({'Level': Repository.get_dict_value(
        {'LOW': 0, 'MEDIUM': 0.5, 'HIGH': 1},
        str(r_sheet.cell(rowx, 6).value).strip().split(';')[1])}
    )
    return info_dict


def character_factor_normalization(src_path, dst_path):
    r_workbook = xlrd.open_workbook(src_path)
    r_sheet = r_workbook.sheet_by_index(0)
    all_cwe_id_list = sorted(Repository.get_all_cwe_id_list())
    Repository.init_workbook(
        dst_path,
        ['Interval', 'Level', 'Score'] + all_cwe_id_list
    )
    for rowx in range(2, r_sheet.nrows):
        print('\rRow Index:' + str(rowx - 1), end='')
        info_dict = get_info_dict(r_sheet, rowx, all_cwe_id_list)
        Repository.write_workbook(dst_path, info_dict, rowx - 1)


if __name__ == '__main__':
    character_factor_normalization(
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Data\Linux Kernel Character Factor(Middle).xls',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Data\Linux Kernel Character Factor(Middle)(Normal).xls'
    )
