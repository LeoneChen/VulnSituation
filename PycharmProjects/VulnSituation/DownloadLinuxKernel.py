# Author: 14281055 Liheng Chen CIT BJTU
# File Name: DownloadLinuxKernel.py


import Repository
import random
import bs4
import os
import re


def download_certain_version_number_linux_kernel(hyperlink, save_dir):
    content = Repository.requests_get_content(hyperlink, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        soup = bs4.BeautifulSoup(content, 'lxml')
        version_number_downloaded_list = []
        for tag_a in soup.select('a'):
            match = re.match('linux-(\d+(.\d+)*)\.tar.*', tag_a.get_text(), re.I)
            if match and match.group(1) not in version_number_downloaded_list:
                print('\rDownload:\033[4;34m' + match.group() + '\033[0m', end='')
                Repository.download_file_in_chunk(hyperlink + tag_a['href'],
                                                  os.path.join(save_dir, tag_a.get_text()))
                version_number_downloaded_list.append(match.group(1))
        return True
    return False


def download_linux_kernel(save_dir, linux_kernel_series):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    linux_kernel_root_url = 'https://mirrors.edge.kernel.org/pub/linux/kernel/'
    content = Repository.requests_get_content(linux_kernel_root_url, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_a in soup.select('a'):
            # if re.match(r'v\d+\.[\dx]', tag_a.get_text().strip(), re.I):
            if re.match(linux_kernel_series, tag_a.get_text().strip(), re.I):
                if not download_certain_version_number_linux_kernel(linux_kernel_root_url + tag_a['href'],
                                                                    save_dir):
                    print('\r\033[1;31mFail:' + tag_a.get_text().strip() + '\033[0m')
        return True
    return False


if __name__ == '__main__':
    download_linux_kernel(r'D:\Linux Kernel\All Zip', r'v\d+\.(\d+|x)')
