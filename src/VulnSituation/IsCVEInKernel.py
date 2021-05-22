# Author: 14281055 Liheng Chen CIT BJTU
# File Name: IsCVEInKernel
import VersionNumberAndExistTime
import os

if __name__ == '__main__':
    cve_id = str(input('CVE ID:'))
    info_tuple = VersionNumberAndExistTime.get_version_number_and_exist_time_tuple(
        os.path.join(r'C:\Users\79196\Downloads\NVD\Linux Kernel Patch', cve_id),
        r'D:\Linux Kernel\All',
        r'C:\Users\79196\Downloads\NVD\Linux Kernel Release Time.xls'
    )
    if info_tuple:
        print(info_tuple[0])
    else:
        print('\rNo Info')
