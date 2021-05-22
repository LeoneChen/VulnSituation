# Author: 14281055 Liheng Chen CIT BJTU
# File Name: LinuxKernelReleaseTime.py


import Repository
import random
import bs4
import os
import re
import datetime


def update_oldest_release_time(version_release_time_dict, version_number, release_time):
    if isinstance(version_release_time_dict, dict) or Repository.is_version_number(version_number):
        if version_number in version_release_time_dict.keys():
            if release_time < version_release_time_dict[version_number]:
                version_release_time_dict[version_number] = release_time
        else:
            version_release_time_dict.update({version_number: release_time})
        return True
    return False


def get_version_number_release_time_dict(hyperlink):
    content = Repository.requests_get_content(hyperlink, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    version_number_release_time_dict = {}
    if content:
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_pre in soup.select('pre'):
            for version_number_release_time_tuple in re.findall(
                    'linux-(\d+(.\d+)*)\.tar.*?(\d+-\w+-\d+ \d+:\d+)',
                    tag_pre.get_text().strip()):
                version_number = version_number_release_time_tuple[0]
                try:
                    release_time = datetime.datetime.strptime(version_number_release_time_tuple[2],
                                                              "%d-%b-%Y %H:%M")
                except ValueError:
                    continue
                update_oldest_release_time(version_number_release_time_dict, version_number, release_time)
    return version_number_release_time_dict


def save_linux_kernel_release_time(save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, 'Linux Kernel Release Time.xls')
    Repository.init_workbook(save_path, ['Version Number', 'Release Time'])
    start_row_index = 1
    linux_kernel_root_url = 'https://mirrors.edge.kernel.org/pub/linux/kernel/'
    content = Repository.requests_get_content(linux_kernel_root_url, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_a in soup.select('a'):
            if re.match(r'v\d+\.(\d+|x)', tag_a.get_text().strip(), re.I):
                version_number_release_time_dict = get_version_number_release_time_dict(
                    linux_kernel_root_url + tag_a['href'])
                if version_number_release_time_dict:
                    Repository.write_workbook_key_value(save_path, version_number_release_time_dict,
                                                        start_row_index, [None, Repository.set_date_style()])
                    start_row_index += len(version_number_release_time_dict)
                else:
                    print('\033[1;31mFail:' + tag_a.get_text().strip() + '\033[0m')
        return True
    return False


if __name__ == '__main__':
    save_linux_kernel_release_time(r'C:\Users\陈力恒\Downloads\NVD')
