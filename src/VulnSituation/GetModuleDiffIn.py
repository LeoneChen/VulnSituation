# Author: 14281055 Liheng Chen CIT BJTU
# File Name: GetModuleDiffIn.py
import Repository
import re
import os


def match_line(module_info_list, line):
    line = Repository.separate_word_and_nonword(line)
    if module_info_list[0] == 'struct':
        return True if re.search(r'\bstruct ' + re.escape(module_info_list[1]) + ' {', line) else False
    elif module_info_list[0] == 'function':
        return True if re.search(
            r'\b' + re.escape(module_info_list[1]) + ' ' + re.escape(module_info_list[2]) + r' \(',
            line) else False
    return None


def match_lines(module_info_list, line_list, default_line_index_range=30):
    if match_line(module_info_list, line_list[0]):
        return True
    line_index_range = default_line_index_range if len(line_list) > default_line_index_range else len(
        line_list)
    lines = Repository.line_list_to_lines(line_list[:line_index_range])
    first_line_end_index = Repository.get_first_line_end_index_in_lines(line_list[0], lines)
    if module_info_list[0] == 'struct':
        match = re.search(r'\bstruct ' + re.escape(module_info_list[1]) + ' {', lines)
        if match:
            tag_end_index = match.start() + 5  # length of 'struct' is 6
            if tag_end_index <= first_line_end_index:
                return True
        return False
    elif module_info_list[0] == 'function':
        match = re.search(
            r'\b' + re.escape(module_info_list[1]) + ' (?:\* )*' + re.escape(
                module_info_list[2]) + r' \([^)]*\) {',
            lines)
        if match:
            tag_end_index = match.start() + len(module_info_list[1]) - 1
            if tag_end_index <= first_line_end_index:
                return True
        return False
    return None


def get_module_info_list(line_list):
    lines = Repository.line_list_to_lines(line_list)
    first_line_end_index = Repository.get_first_line_end_index_in_lines(line_list[0], lines)
    match = re.search(r'\bstruct (\w+) {', lines)
    if match:
        tag_end_index = match.start() + 5  # length of 'struct' is 6
        if tag_end_index <= first_line_end_index:
            return ['struct', match.group(1)]

    match = re.search(r'(?!if|while)(\w+) (?:\* )*(?!if|while)(\w+) \([^)]*\) {', lines)
    if match:
        tag_end_index = match.start() + len(match.group(1)) - 1
        if tag_end_index <= first_line_end_index:
            return ['function', match.group(1), match.group(2)]
    return None


def read_module_and_scope(module_file_path, line_index):
    line = Repository.get_file_line_list(module_file_path)[line_index]
    if line.strip() == '':
        return []
    else:
        module_and_scope = line.strip().split('\t')
        module_and_scope[-2] = int(module_and_scope[-2])
        module_and_scope[-1] = int(module_and_scope[-1])
        return module_and_scope


def read_module_and_scope_list(module_file_path):
    module_file_line_list = Repository.get_file_line_list(module_file_path)
    module_and_scope_list = []
    if module_file_line_list:
        for line in module_file_line_list:
            module_and_scope = line.strip().split('\t')
            module_and_scope[-2] = int(module_and_scope[-2])
            module_and_scope[-1] = int(module_and_scope[-1])
            module_and_scope_list.append(module_and_scope)
    return module_and_scope_list


# def get_module_info_list_list(dst_file_path, default_line_list_range=30):
#     dst_file_line_list = Repository.get_file_line_list(dst_file_path)
#     module_info_list_list = []
#     for line_index, line in enumerate(dst_file_line_list):
#         line_list_range = default_line_list_range if len(
#             dst_file_line_list) - line_index > default_line_list_range else len(
#             dst_file_line_list) - line_index
#         module = get_module_info_list(dst_file_line_list[line_index:line_index + line_list_range])
#         if module:
#             module_info_list_list.append(module)
#     return module_info_list_list


def get_module_and_scope_list(dst_file_path, default_line_list_range=30, write_flag=False):
    module_file_path = Repository.add_prefix_to_file_name(dst_file_path, '(Module)')
    is_module_file_exist = True if os.path.exists(module_file_path) else False
    dst_file_line_list = Repository.get_file_line_list(dst_file_path)
    module_and_scope_list = []
    for line_index, line in enumerate(dst_file_line_list):
        line_list_range = default_line_list_range if len(
            dst_file_line_list) - line_index > default_line_list_range else len(
            dst_file_line_list) - line_index
        module = get_module_info_list(dst_file_line_list[line_index:line_index + line_list_range])
        if module:
            scope = get_module_scope(module, dst_file_path, line_index)
            if not scope:
                scope = [None, None]
            module_and_scope = module + scope
            module_and_scope_list.append(module_and_scope)
            if write_flag and not is_module_file_exist:
                line = '\t'.join(module_and_scope[:-2]) + '\t' + str(module_and_scope[-2]) + '\t' + str(
                    module_and_scope[-1])
                Repository.append_file_with_eol(module_file_path, line)
    return module_and_scope_list


def print_module_and_scope(file_path):
    for module_and_scope in get_module_and_scope_list(file_path):
        print('\t'.join(module_and_scope[:-2]) + '\t' + str(module_and_scope[-2]) + '\t' + str(
            module_and_scope[-1]))


def write_module_and_scope(module_file_path, module_and_scope=None, flag=False):
    if flag:
        line = '\t'.join(module_and_scope[:-2]) + '\t' + str(module_and_scope[-2]) + '\t' + str(
            module_and_scope[-1])
        Repository.append_file_with_eol(module_file_path, line)
    else:
        Repository.append_file_with_eol(module_file_path, '')


def write_module_file(dst_file_path):
    module_file_path = Repository.add_prefix_to_file_name(dst_file_path, '(Module)')
    if not os.path.exists(module_file_path):
        get_module_and_scope_list(dst_file_path, write_flag=True)


def write_module_diff_file(diff_file_path):
    module_diff_file_path = Repository.add_prefix_to_file_name(diff_file_path, '(Module)')
    if not os.path.exists(module_diff_file_path):
        bm_file_path = Repository.add_prefix_to_file_name(diff_file_path, '(BM)')
        write_module_file(bm_file_path)
        for diff_segment in get_diff_segment_list(diff_file_path):
            for module_and_scope in read_module_and_scope_list(
                    Repository.add_prefix_to_file_name(bm_file_path, '(Module)')):
                if module_and_scope[-2] != 'None' and module_and_scope[-1] != 'None' \
                        and Repository.is_lines_in_lines(diff_segment[4],
                                                         Repository.get_file_line_list(bm_file_path)
                                                         [module_and_scope[-2]: module_and_scope[-1] + 1]):
                    write_module_and_scope(module_diff_file_path, module_and_scope, True)
                    break
            else:
                write_module_and_scope(module_diff_file_path)


def is_diff_segment_in_lines(diff_segment, dst_line_list, has_module_info=True):
    if not has_module_info and diff_segment[1] == []:
        return Repository.unknown
    else:
        return Repository.true if Repository.is_lines_in_lines(diff_segment[1], dst_line_list) \
                                  and not Repository.is_lines_in_lines(diff_segment[2],
                                                                       dst_line_list) else Repository.false


def get_module_scope(module, dst_file_path, line_offset=0):
    dst_file_line_list = Repository.get_file_line_list(dst_file_path)
    for line_index in range(len(dst_file_line_list[line_offset:])):
        if match_lines(module, dst_file_line_list[line_offset + line_index:]):
            start_line_index = line_offset + line_index
            break
    else:
        return []
    remain_lines = Repository.line_list_to_lines(dst_file_line_list[start_line_index:])
    remain_line_end_char_index_dict = Repository.get_line_end_char_index_dict_with_lines(
        dst_file_line_list[start_line_index:],
        remain_lines)
    opening_brace_number = 0
    closing_brace_number = 0
    match = re.search(re.escape(module[-1]) + '.*?{', remain_lines)
    if match:
        # opening_brace_line_index = Repository.get_line_index(remain_line_end_char_index_dict,
        #                                                      match.end() - 1) + start_line_index
        opening_brace_number += 1
    else:
        return []
    closing_brace_line_index = len(dst_file_line_list)
    for char_index, character in enumerate(remain_lines[match.end():]):
        if character == '{':
            opening_brace_number += 1
        elif character == '}':
            closing_brace_number += 1
            if opening_brace_number == closing_brace_number:
                closing_brace_line_index = Repository.get_line_index(
                    remain_line_end_char_index_dict,
                    char_index + match.end()
                ) + start_line_index
                break
    return [start_line_index, closing_brace_line_index]


def get_diff_segment_list(diff_file_path):
    diff_file_line_list = Repository.get_file_line_list(diff_file_path)
    diff_segment_list = []
    diff_segment = []
    diff_segment_delete_list = []
    diff_segment_add_list = []
    diff_segment_other_list = []
    diff_segment_non_add_list = []
    has_diff_segment_head = False
    for diff_file_line in diff_file_line_list:
        match = re.search(r'@@.*?@@(.*)', diff_file_line)
        if match:
            if diff_segment:
                diff_segment.append(diff_segment_delete_list)
                diff_segment.append(diff_segment_add_list)
                diff_segment.append(diff_segment_other_list)
                diff_segment.append(diff_segment_non_add_list)
                diff_segment_list.append(diff_segment)
                diff_segment_delete_list = []
                diff_segment_add_list = []
                diff_segment_other_list = []
                diff_segment_non_add_list = []
                diff_segment = []
            diff_segment_head = match.group(1).strip()
            diff_segment.append(diff_segment_head)
            has_diff_segment_head = True
        else:
            if has_diff_segment_head and diff_file_line.strip() != '':
                match = re.match(r'\+(.*)', diff_file_line)
                if match:
                    diff_segment_add_list.append(match.group(1).strip())
                elif re.match(r'[^-+]', diff_file_line):
                    diff_segment_other_list.append(diff_file_line.strip())
                    diff_segment_non_add_list.append(diff_file_line.strip())
                else:
                    match = re.match(r'-(.*)', diff_file_line)
                    if match:
                        diff_segment_delete_list.append(match.group(1).strip())
                        diff_segment_non_add_list.append(match.group(1).strip())
    if diff_segment:
        diff_segment.append(diff_segment_delete_list)
        diff_segment.append(diff_segment_add_list)
        diff_segment.append(diff_segment_other_list)
        diff_segment.append(diff_segment_non_add_list)
        diff_segment_list.append(diff_segment)
    return diff_segment_list

# def write_diff_module_and_scope_tuple(diff_file_path):
#     bm_file_path = os.path.join(os.path.dirname(diff_file_path), '(BM)' + os.path.basename(diff_file_path))
#     save_path = os.path.join(os.path.dirname(diff_file_path), '(Module)' + os.path.basename(diff_file_path))
#     if os.path.exists(save_path):
#         os.remove(save_path)
#     bm_file_line_list = Repository.get_file_line_list(bm_file_path)
#     for diff in get_diff_list(diff_file_path):
#         diff_module_and_scope_tuple = get_diff_module_and_scope_tuple(diff[1:], bm_file_line_list)
#         string = '\t'.join(diff_module_and_scope_tuple[0])
#         string += '\t'
#         string += '\t'.join(
#             [str(diff_module_and_scope_tuple[1]), str(diff_module_and_scope_tuple[2])]
#         )
#         Repository.append_file_with_eol(save_path, string)
#
#
# def write_all_diff_module_and_scope_tuple(patch_root):
#     for patch_dir_name in os.listdir(patch_root):
#         patch_dir_path = os.path.join(patch_root, patch_dir_name)
#         if os.path.isdir(patch_dir_path):
#             for file_name in os.listdir(patch_dir_path):
#                 if not re.match(r'\(', file_name) and not re.match(r'Source\.txt', file_name):
#                     write_diff_module_and_scope_tuple(os.path.join(patch_dir_path, file_name))
