# Author: Liheng Chen
# File Name:
import Repository
import os
import re
import GetModuleDiffIn
import VersionNumberAndExistTime


def is_diff_segment_in_files(diff_segment, diff_segment_index, project_dir_path, diff_file_path):
    for file_path in Repository.get_all_file_path_list(project_dir_path):
        result = VersionNumberAndExistTime.is_diff_segment_in_file(diff_segment, diff_segment_index, file_path,
                                                                   diff_file_path)
        if result == Repository.unknown:
            print('\rUnknown ' + file_path, end='')
            return Repository.unknown
        elif result == Repository.true:
            print('\rIn ' + file_path)
            return Repository.true
        else:
            print('\rNot In ' + file_path, end='')
    return Repository.false


def is_diff_in_project_2(diff_file_path, project_dir_path):
    unknown_flag = True
    print(os.path.basename(diff_file_path))
    for diff_segment_index, diff_segment in enumerate(GetModuleDiffIn.get_diff_segment_list(diff_file_path)):
        result = is_diff_segment_in_files(diff_segment, diff_segment_index, project_dir_path, diff_file_path)
        if Repository.false == result:
            return False
        elif Repository.true == result:
            unknown_flag = False
    if unknown_flag:
        return False
    else:
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


def is_file_name_legal(file_name):
    return True if file_name != 'Source.txt' and not re.match(r'\(', file_name) else False


def is_cve_in_project(cve_dir_path, project_dir_path):
    if Repository.is_dir_empty(cve_dir_path):
        return False
    for file_name in os.listdir(cve_dir_path):
        if is_file_name_legal(file_name) \
                and not VersionNumberAndExistTime.is_one_vuln_in_linux_kernel_accurate(
            os.path.join(cve_dir_path, file_name), project_dir_path):
            return False
    return True


def get_linux_kernel_accurate_dir(project_dir):
    for file_name in os.listdir(project_dir):
        if re.match('linux', file_name, re.I):
            project_dir = os.path.join(project_dir, file_name)
            break
    return project_dir


def is_cve_in_projects(cve_dir, projects_dir):
    print(os.path.basename(cve_dir) + ':')
    for project_name in os.listdir(projects_dir):
        project_dir = get_linux_kernel_accurate_dir(os.path.join(projects_dir, project_name))
        print('\t' + project_name+': ' + str(is_cve_in_project(cve_dir, project_dir)))


if __name__ == '__main__':
    is_cve_in_projects(
        r'E:\Linux Kernel Patch\CVE-2018-7995',
        r'E:\Linux')
