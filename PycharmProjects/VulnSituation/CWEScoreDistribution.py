# Author: 14281055 Liheng Chen CIT BJTU
# File Name:
import xlrd
import Repository


def cwe_score_distribution(src_path, dst_path):
    r_workbook = xlrd.open_workbook(src_path)
    r_sheet = r_workbook.sheet_by_index(0)
    all_cwe_id_dict = {}
    for row_index in range(1, r_sheet.nrows):
        cwe_id = int(r_sheet.cell(row_index, 3).value)
        level = int(r_sheet.cell(row_index, 4).value)
        score = float(r_sheet.cell(row_index, 5).value)
        if cwe_id in all_cwe_id_dict.keys():
            cve_id_dict = all_cwe_id_dict[cwe_id]
            cve_id_dict[level] += 1
            cve_id_dict['Score Impact'] += score
        else:
            cve_id_dict = {1: 0, 2: 0, 3: 0, 'Score Impact': 0}
            cve_id_dict[level] += 1
            cve_id_dict['Score Impact'] += score
            all_cwe_id_dict.update({cwe_id: cve_id_dict})
    Repository.init_workbook(dst_path, ['CWE ID', 'Low', 'Medium', 'High', 'Score Impact', 'Level Impact'])
    for cwe_id_index, cwe_id in enumerate(all_cwe_id_dict.keys()):
        cve_id_dict = all_cwe_id_dict[cwe_id]
        Repository.write_workbook(
            dst_path,
            {
                'CWE ID': 'CWE-' + str(cwe_id if cwe_id != -1 else 'Other'),
                'Low': cve_id_dict[1],
                'Medium': cve_id_dict[2],
                'High': cve_id_dict[3],
                'Score Impact': cve_id_dict['Score Impact'],
                'Level Impact': 1 * cve_id_dict[1] + 2 * cve_id_dict[2] + 3 * cve_id_dict[3]
            },
            cwe_id_index + 1
        )


if __name__ == '__main__':
    cwe_score_distribution(r'C:\Users\79196\Downloads\NVD\Linux Kernel Character Factor(Simplify).xls',
                           r'C:\Users\79196\Downloads\NVD\Linux Kernel CWE Score Distribution.xls')
