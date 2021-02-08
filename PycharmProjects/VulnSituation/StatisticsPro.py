# Author: 14281055 Liheng Chen CIT BJTU
# File Name: StatisticsPro.py


import xlrd
import re
import Repository
from xlutils.copy import copy


def write_book(save_path, count_dict_by_year):
    r_workbook = xlrd.open_workbook(save_path, formatting_info=True)
    r_sheet = r_workbook.sheets()[0]
    w_workbook = copy(r_workbook)
    w_sheet = w_workbook.get_sheet(0)
    row_index = 1
    for year in count_dict_by_year.keys():
        w_sheet.write(row_index, 0, year)
        for col_index in range(1, r_sheet.ncols):
            head = str(r_sheet.cell(0, col_index).value).strip()
            count_dict = count_dict_by_year[year]

            if head in count_dict.keys():
                w_sheet.write(row_index, col_index, count_dict[head])
            else:
                w_sheet.write(row_index, col_index, 0)
        row_index += 1

    w_workbook.save(save_path)


def get_cve_info_tuple(r_sheet, row_index):
    match_cve_id = re.search('CVE-(\d+)', str(r_sheet.cell(row_index, 0).value).strip(), re.I)
    if match_cve_id:
        year = match_cve_id.group(1)
    else:
        year = None
    match_cwe_id = re.search('\(([^()]*?)\)$', str(r_sheet.cell(row_index, 5).value).strip(), re.I)
    if match_cwe_id:
        cwe_id = match_cwe_id.group(1)
    else:
        cwe_id = 'NVD-CWE-noinfo'
    base_score = 'Base Score-' + str(r_sheet.cell(row_index, 6).value).strip().split(';')[1].title()
    av = 'Attack Vector-' + str(r_sheet.cell(row_index, 7).value).strip().title()
    ac = 'Access Complexity-' + str(r_sheet.cell(row_index, 8).value).strip().title()
    au = 'Authentication-' + str(r_sheet.cell(row_index, 9).value).strip().title()
    ci = 'Confidentiality Impact-' + str(r_sheet.cell(row_index, 10).value).strip().title()
    ii = 'Integrity Impact-' + str(r_sheet.cell(row_index, 11).value).strip().title()
    ai = 'Availability Impact-' + str(r_sheet.cell(row_index, 12).value).strip().title()
    return year, cwe_id, base_score, av, ac, au, ci, ii, ai


def statistics(source_path, destination_path):
    r_workbook = xlrd.open_workbook(source_path)
    r_sheet = r_workbook.sheets()[0]
    heads = ['Year', 'Base Score-High', 'Base Score-Medium', 'Base Score-Low',
             'Attack Vector-Local', 'Attack Vector-Adjacent Network', 'Attack Vector-Network',
             'Access Complexity-High', 'Access Complexity-Medium', 'Access Complexity-Low',
             'Authentication-Multiple', 'Authentication-Single', 'Authentication-None',
             'Confidentiality Impact-None', 'Confidentiality Impact-Partial',
             'Confidentiality Impact-Complete',
             'Integrity Impact-None', 'Integrity Impact-Partial', 'Integrity Impact-Complete',
             'Availability Impact-None', 'Availability Impact-Partial', 'Availability Impact-Complete']
    all_cwe_id_list = Repository.get_all_cwe_id_list()
    all_cwe_id_list.sort()
    heads.extend(all_cwe_id_list)
    Repository.init_workbook(destination_path, heads, width=1)
    character_factor_count_dict_by_year = {}
    for row_index in range(2, r_sheet.nrows):
        cve_info_tuple = get_cve_info_tuple(r_sheet, row_index)
        if not cve_info_tuple[0]:
            continue
        elif cve_info_tuple[0] in character_factor_count_dict_by_year.keys():
            Repository.update_count_dict(character_factor_count_dict_by_year[cve_info_tuple[0]],
                                         cve_info_tuple[1:])
        else:
            character_factor_count_dict_by_year.update({cve_info_tuple[0]: {}})
            Repository.update_count_dict(character_factor_count_dict_by_year[cve_info_tuple[0]],
                                         cve_info_tuple[1:])
    write_book(destination_path, character_factor_count_dict_by_year)


if __name__ == '__main__':
    statistics(r'C:\Users\79196\Downloads\NVD\Linux Kernel Character Factor.xls',
               r'C:\Users\79196\Downloads\NVD\Linux Kernel Character Factor Statistics.xls')
