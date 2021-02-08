# Author: 14281055 Liheng Chen CIT BJTU
# File Name:
import Repository
import os
import re
import GetModuleDiffIn
import VersionNumberAndExistTime


def is_diff_segment_in_files(diff_segment, diff_segment_index, project_dir_path, diff_file_path):
    for file_path in Repository.get_all_file_path_list(project_dir_path):
        if VersionNumberAndExistTime.is_diff_segment_in_file(diff_segment, diff_segment_index, file_path,
                                                             diff_file_path):
            print('\rIn ' + file_path)
            return True
        print('\rNot In ' + file_path, end='')
    return False


def is_diff_in_project_2(diff_file_path, project_dir_path):
    print(os.path.basename(diff_file_path))
    for diff_segment_index, diff_segment in enumerate(GetModuleDiffIn.get_diff_segment_list(diff_file_path)):
        if not is_diff_segment_in_files(diff_segment, diff_segment_index, project_dir_path, diff_file_path):
            return False
    return True


def is_diff_in_project(diff_file_path, project_dir_path):
    for file_path in Repository.get_all_file_path_list(project_dir_path):
        for diff_segment_index, diff_segment in enumerate(
                GetModuleDiffIn.get_diff_segment_list(diff_file_path)):
            if not VersionNumberAndExistTime.is_diff_segment_in_file(diff_segment, diff_segment_index,
                                                                     file_path,
                                                                     diff_file_path):
                print('\r' + diff_file_path.split('~!@#')[-1] + ' Not In ' + file_path, end='')
                break
        else:
            print('\r' + diff_file_path.split('~!@#')[-1] + ' In ' + file_path)
            return True
    return False


def is_cve_in_project(cve_dir_path, project_dir_path):
    if Repository.is_dir_empty(cve_dir_path):
        return False
    for file_name in os.listdir(cve_dir_path):
        if file_name != 'Source.txt' and not re.match(r'\(', file_name) \
                and not is_diff_in_project_2(os.path.join(cve_dir_path, file_name), project_dir_path):
            return False
    return True


if __name__ == '__main__':
    print(is_cve_in_project(r'C:\Users\79196\Downloads\NVD\Linux Kernel Patch\CVE-2018-7995',
                            r'D:\Linux Kernel\All\linux-3.3\linux-3.3'))
