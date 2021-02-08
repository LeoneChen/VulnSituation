# Author: 14281055 Liheng Chen CIT BJTU
# File Name:
import os
import Repository


def patch_source_statistics(patch_root_path):
    git_kernel_org_count = 0
    patchwork_kernel_org_count = 0
    github_com_count = 0
    for patch_dir_name in os.listdir(patch_root_path):
        patch_dir_path = os.path.join(patch_root_path, patch_dir_name)
        if os.path.isdir(patch_dir_path):
            for file_name in os.listdir(patch_dir_path):
                if file_name == 'Source.txt':
                    patch_source = Repository.get_file_line_list(os.path.join(patch_dir_path, file_name))[
                        0].strip()
                    if patch_source == 'git.kernel.org':
                        git_kernel_org_count += 1
                    elif patch_source == 'patchwork.kernel.org':
                        patchwork_kernel_org_count += 1
                    elif patch_source == 'github.com':
                        github_com_count += 1
    all_count = git_kernel_org_count + patchwork_kernel_org_count + github_com_count
    print('git.kernel.org:\t%d\t%d%%' % (git_kernel_org_count, int(git_kernel_org_count / all_count * 100)))
    print('patchwork.kernel.org:\t%d\t%d%%' % (
        patchwork_kernel_org_count, int(patchwork_kernel_org_count / all_count * 100)))
    print('github.com:\t%d\t%d%%' % (github_com_count, int(github_com_count / all_count * 100)))


if __name__ == '__main__':
    patch_source_statistics(r'C:\Users\79196\Downloads\NVD\Linux Kernel Patch')
