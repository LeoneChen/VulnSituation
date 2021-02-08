# Author: 14281055 Liheng Chen CIT BJTU
# File Name: AddOSS.py


import Repository


def get_category_abbr(category):
    if category == 'Web Server':
        return 'WEB'
    elif category == 'Database':
        return 'DB'
    elif category == 'E-Mail':
        return 'EM'
    elif category == 'Security Product':
        return 'SP'
    elif category == 'Development Kit':
        return 'DK'
    elif category == 'Application':
        return 'APP'
    else:
        print('\033[1;31mUnknown Category\033[0m')
        return None


def get_oss_info_dict(key_word):
    oss_info_dict = {
        'Key Word': key_word,
        'NVD Records Count': Repository.get_cve_count(key_word)
    }
    print('NVD Records Count:' + str(oss_info_dict['NVD Records Count']))
    if oss_info_dict['NVD Records Count'] < 10:
        print('\033[1;31mNVD Too Few\033[0m')
        return []
    oss_info_dict.update({'Description': Repository.get_description_in_baidubaike(key_word)})
    oss_info_dict.update({'Category': input('Category:').title()})
    if oss_info_dict['Category'] == '':
        oss_info_dict['Category'] = 'Application'
    oss_info_dict.update({'Name': input('Detail Name(Optional):').title()})
    if oss_info_dict['Name'] == '':
        oss_info_dict['Name'] = oss_info_dict['Key Word']
    oss_info_dict.update({'Note': input('Note(Optional):')})
    return oss_info_dict


def add_oss(save_path):
    # Get key word
    key_word = input('Key Word:').title()
    if key_word:
        oss_info_dict = get_oss_info_dict(key_word)
        if oss_info_dict:
            category_abbr = get_category_abbr(oss_info_dict['Category'])
            if category_abbr:
                Repository.init_workbook(
                    save_path,
                    ['Number', 'Name', 'Key Word', 'Description', 'NVD Records Count', 'Note'],
                    sheet_name_list=['Web Server', 'Database', 'E-Mail', 'Security Product',
                                     'Development Kit', 'Application']
                )
                row_index = Repository.get_sheet_nrows_by_name(save_path, oss_info_dict['Category'])
                oss_info_dict.update({'Number': 'OSS-' + category_abbr + '-' + str(row_index)})
                Repository.write_workbook(save_path, oss_info_dict, row_index,
                                          sheet_name=oss_info_dict['Category'])
    return False


if __name__ == '__main__':
    add_oss(r'C:\Users\79196\Downloads\NVD\OSSList(V2).xls')
