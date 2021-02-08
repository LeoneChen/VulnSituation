# Author: 14281055 Liheng Chen CIT BJTU
# File Name:
import xlrd
from xlutils.copy import copy
import NVDVulnInfoCrawler
import Repository


def remove_needless_rows():
    src_path = r'C:\Users\陈力恒\Downloads\漏洞态势感知与预测\工作\Linux Kernel的CVE信息.xls'
    dst_path = r'C:\Users\陈力恒\Downloads\漏洞态势感知与预测\工作\Linux Kernel的CVE信息（筛选）.xls'
    ref_path = r'C:\Users\陈力恒\Downloads\漏洞态势感知与预测\工作\Linux Kernel Character Factor(Middle).xls'

    NVDVulnInfoCrawler.init_workbook(dst_path)
    dst_w_workbook = copy(xlrd.open_workbook(dst_path, formatting_info=True))
    Repository.copy_specified_rows(
        xlrd.open_workbook(src_path).sheet_by_index(0), 2, 0,
        dst_w_workbook.get_sheet(0), 2,
        xlrd.open_workbook(ref_path).sheet_by_index(0).col_values(0, 2),
    )
    dst_w_workbook.save(dst_path)


if __name__ == '__main__':
    remove_needless_rows()
