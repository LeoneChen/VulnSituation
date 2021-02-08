# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import os


def ext_statistics(dir_path):
    file_name_list = os.listdir(dir_path)
    for file_name in file_name_list:
        file_path = os.path.join(dir_path, file_name)
        if os.path.isdir(file_path):
            ext_statistics(file_path)
        else:
            ext = os.path.splitext(file_path)[1]
            if ext == '':
                if 'None' in ext_count_dict.keys():
                    ext_count_dict['None'] += 1
                    # print_ext_statistics()
                else:
                    ext_count_dict.update({'None': 1})
                    # print_ext_statistics()
            else:
                if ext in ext_count_dict.keys():
                    ext_count_dict[ext] += 1
                    # print_ext_statistics()
                else:
                    ext_count_dict.update({ext: 1})
                    # print_ext_statistics()


def print_ext_statistics():
    total_count = 0
    for key in ext_count_dict.keys():
        total_count += ext_count_dict[key]
    print('Total Count:' + str(total_count))
    for key in ext_count_dict.keys():
        if int(ext_count_dict[key] / total_count * 100) >= 1:
            print('\033[1;31m%s\033[0m Count:%d Rate:%d%%\t' %
                  (key, ext_count_dict[key], int(ext_count_dict[key] / total_count * 100)))


if __name__ == '__main__':
    ext_count_dict = {}
    ext_statistics(r'D:\Linux Kernel\All\linux-4.0.1')
    print_ext_statistics()
