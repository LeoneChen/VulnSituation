# Author: 14281055 Liheng Chen CIT BJTU
# File Name: CharacterFactor.py

import re
import os
import datetime
import bs4
import random
import xlrd
import xlwt
from xlutils.copy import copy
import Repository


def write_workbook(cve_info_dict, save_path, row_index):
    if 'Linux Kernel Version Number' not in cve_info_dict.keys() \
            or cve_info_dict['Linux Kernel Version Number'] is None:
        # print('\033[1;31mNo version number!\033[0m')
        return False
    r_workbook = xlrd.open_workbook(save_path, formatting_info=True)
    w_workbook = copy(r_workbook)
    w_sheet = w_workbook.get_sheet(0)

    keys = ['CVE Number', 'Linux Kernel Version Number', 'Vulnerability Exist Time',
            'Vulnerability Discover Time', 'Interval Between Exist And Discover', 'Vulnerability Type']
    cvss_v2_keys = ['Base Score', 'Attack Vector', 'Access Complexity', 'Authentication',
                    'Confidentiality Impact', 'Integrity Impact', 'Availability Impact']

    col_index = 0
    for key in keys:
        if key in cve_info_dict.keys():
            if key in ('Vulnerability Exist Time', 'Vulnerability Discover Time'):
                cell_style = Repository.set_date_style(True)
            else:
                cell_style = Repository.set_date_style(False)
            if cve_info_dict[key]:
                w_sheet.write(row_index, col_index, cve_info_dict[key], cell_style)
        else:
            w_sheet.write(row_index, col_index, 'Error', Repository.set_font(color_index=2))
        col_index += 1

    if 'CVSS Severity V2' in cve_info_dict.keys():
        cvss_v2_base_score_and_vector_dict = cve_info_dict['CVSS Severity V2']
        for key in cvss_v2_keys:
            if key in cvss_v2_base_score_and_vector_dict.keys():
                if cvss_v2_base_score_and_vector_dict[key]:
                    w_sheet.write(row_index, col_index, cvss_v2_base_score_and_vector_dict[key])
            else:
                w_sheet.write(row_index, col_index, 'Error', Repository.set_font(color_index=2))
            col_index += 1

    w_workbook.save(save_path)
    return True


def init_workbook(path):
    if os.path.exists(path):
        return False
    w_workbook = xlwt.Workbook()
    w_sheet = w_workbook.add_sheet('Character Factor')

    heads = ['CVE Number', 'Linux Kernel Version Number', 'Vulnerability Exist Time',
             'Vulnerability Discover Time', 'Interval Between Exist And Discover(Day)', 'Vulnerability Type']
    cvss_head = ['Base Score', 'Attack Vector', 'Access Complexity', 'Authentication',
                 'Confidentiality Impact', 'Integrity Impact', 'Availability Impact']

    start_col_index = 0
    cell_width = w_sheet.col(0).width
    # Write heads
    for col_index in range(start_col_index, start_col_index + len(heads)):
        w_sheet.write_merge(0, 1, col_index, col_index, heads[col_index - start_col_index],
                            Repository.set_font(bold=True))
        w_sheet.col(col_index).width = int(cell_width * 3)
    start_col_index += len(heads)
    # Write CVSS V2 head
    w_sheet.write_merge(
        0, 0,
        start_col_index, start_col_index + len(cvss_head) - 1,
        'CVSS Severity V2', Repository.set_font(bold=True)
    )
    for col_index in range(start_col_index, start_col_index + len(cvss_head)):
        w_sheet.write(1, col_index, cvss_head[col_index - start_col_index], Repository.set_font(bold=True))
        w_sheet.col(col_index).width = int(cell_width * 2)
    w_workbook.save(path)
    return True


def vector_element_to_dict(key, vector, partial_re, parameter_dict):
    match = re.match(r".*?" + partial_re + r":([A-Za-z]+)", vector, re.I)
    if match:
        value = match.group(1)
        if value.upper() in parameter_dict.keys():
            return {key: parameter_dict[value.upper()]}
    return {key: None}


def vector_to_dict(vector):
    vector_dict = \
        vector_element_to_dict('Attack Vector', vector, 'AV',
                               {'L': 'Local', 'A': 'Adjacent Network', 'N': 'Network'})
    vector_dict.update(
        vector_element_to_dict('Access Complexity', vector, '/AC',
                               {'H': 'High', 'M': 'Medium', 'L': 'Low'}))
    vector_dict.update(
        vector_element_to_dict('Authentication', vector, '/AU',
                               {'M': 'Multiple', 'S': 'Single', 'N': 'None'}))
    vector_dict.update(
        vector_element_to_dict('Confidentiality Impact', vector, '/C',
                               {'N': 'None', 'P': 'Partial', 'C': 'Complete'}))
    vector_dict.update(
        vector_element_to_dict('Integrity Impact', vector, '/I',
                               {'N': 'None', 'P': 'Partial', 'C': 'Complete'}))
    vector_dict.update(
        vector_element_to_dict('Availability Impact', vector, '/A',
                               {'N': 'None', 'P': 'Partial', 'C': 'Complete'}))
    return vector_dict


def get_cvss_v2_vector_dict(soup):
    for tag_dd in soup.select(
            'p[data-testid=vuln-cvssv2-score-container] span[data-testid=vuln-cvssv2-vector]'):
        match = re.search(r'\((.*?)\)', tag_dd.get_text().strip())
        if match:
            return vector_to_dict(match.group(1))
    return {'Base Score': None, 'Attack Vector': None, 'Access Complexity': None, 'Authentication': None,
            'Confidentiality Impact': None, 'Integrity Impact': None, 'Availability Impact': None}


def get_cvss_v2_base_score(soup):
    for tag_span_score in soup.select(
            'p[data-testid=vuln-cvssv2-score-container] span[data-testid=vuln-cvssv2-base-score]'):
        base_score = tag_span_score.get_text().strip()
        base_score_severity = ''
        for tag_span_severity in soup.select(
                'p[data-testid=vuln-cvssv2-score-container] span[data-testid=vuln-cvssv2-base-score-severity]'
        ):
            base_score_severity = tag_span_severity.get_text().strip()
        return base_score + ';' + base_score_severity
    return None


def get_cvss_v2_base_score_and_vector_dict(base_soup):
    cvss_v2_base_score_and_vector_dict = {'Base Score': get_cvss_v2_base_score(base_soup)}
    cvss_v2_base_score_and_vector_dict.update(get_cvss_v2_vector_dict(base_soup))
    return cvss_v2_base_score_and_vector_dict


def get_linux_kernel_release_time_tuple(version_number, linux_kernel_release_time_file_path):
    r_sheet = xlrd.open_workbook(linux_kernel_release_time_file_path).sheet_by_index(0)
    for row_index in range(1, r_sheet.nrows):
        cell_version_number = r_sheet.cell(row_index, 0).value
        if Repository.is_version_number(cell_version_number) and Repository.version_number_compare(
                version_number, cell_version_number) == 0:
            return xlrd.xldate_as_tuple(r_sheet.cell(row_index, 1).value, 0)[0:3]
    return ()


def get_linux_kernel_release_time_tuple_proximate(version_number, linux_kernel_release_time_file_path):
    r_workbook = xlrd.open_workbook(linux_kernel_release_time_file_path)
    r_sheet = r_workbook.sheets()[0]
    if r_sheet.nrows <= 1:
        return ()
    proximate_version_number = r_sheet.cell(1, 0).value
    proximate_version_number_row_index = 1
    for row_index in range(1, r_sheet.nrows):
        cell_version_number = r_sheet.cell(row_index, 0).value
        if not Repository.is_version_number(cell_version_number):
            continue
        if Repository.version_number_compare(cell_version_number, version_number) == 0:
            proximate_version_number_row_index = row_index
            break
        if Repository.version_number_compare(cell_version_number, version_number) < 0 < \
                Repository.version_number_compare(cell_version_number, proximate_version_number):
            proximate_version_number = cell_version_number
            proximate_version_number_row_index = row_index
    return xlrd.xldate_as_tuple(r_sheet.cell(proximate_version_number_row_index, 1).value, 0)[0:3]


def get_version_number_from_cpe(cpe):
    match = re.search(r'cpe.*?linux:linux_kernel:(\d+(\.\d+)*):', cpe.strip(), re.I)
    if match:
        return match.group(1)
    else:
        return None


def get_vuln_exist_time_tuple_and_version_number(cve_info_url):
    cpe_url = cve_info_url + '/cpes?expandCpeRanges=true'
    content = Repository.requests_get_content(cpe_url, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        url_soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_input in url_soup.select('input#cveTreeJsonDataHidden'):
            value = tag_input.get('value')
            if value:
                value = value.replace('&quot;', '\'').replace('%3a', ':')
                linux_kernel_version_number_list = []
                for cpe in re.findall(r'[\'\"]\s*Uri\s*[\'\"]\s*:\s*[\'\"]\s*cpe.*?linux_kernel.*?[\'\"]',
                                      value, re.I):
                    version_number = get_version_number_from_cpe(cpe)
                    if version_number:
                        linux_kernel_version_number_list.append(version_number)

                oldest_version_number = Repository.get_oldest_version_number(linux_kernel_version_number_list)
                if oldest_version_number:
                    return get_linux_kernel_release_time_tuple(
                        oldest_version_number,
                        g_linux_kernel_release_time_file_path
                    ), oldest_version_number
    return ()


def get_vuln_discover_time(soup):
    reference_dict_list = Repository.get_reference_dict_list(soup)
    for reference_dict in reference_dict_list:
        reference_hyperlink = reference_dict['Hyperlink']
        if re.match(r'https?://git\.kernel\.org', reference_hyperlink, re.I):
            vuln_discover_time = get_vuln_discover_time_in_git(reference_hyperlink)
            if vuln_discover_time:
                return vuln_discover_time
            else:
                continue
        elif re.match(r'https?://patchwork\.kernel\.org', reference_hyperlink, re.I):
            vuln_discover_time = get_vuln_discover_time_in_patchwork(reference_hyperlink)
            if vuln_discover_time:
                return vuln_discover_time
            else:
                continue
        elif re.match(r'https?://github\.com', reference_hyperlink, re.I):
            vuln_discover_time = get_vuln_discover_time_in_github(reference_hyperlink)
            if vuln_discover_time:
                return vuln_discover_time
            else:
                continue

    return get_cve_publish_date(soup)


def get_cve_info_dict(cve_info_url):
    cve_info_dict = {}
    vuln_exist_time_tuple_and_version_number = get_vuln_exist_time_tuple_and_version_number(cve_info_url)
    if vuln_exist_time_tuple_and_version_number:
        if vuln_exist_time_tuple_and_version_number[0]:
            cve_info_dict.update(
                {"Vulnerability Exist Time": datetime.datetime(
                    *(vuln_exist_time_tuple_and_version_number[0]))})
        else:
            cve_info_dict.update({"Vulnerability Exist Time": None})
        cve_info_dict.update({"Linux Kernel Version Number": vuln_exist_time_tuple_and_version_number[1]})
    else:
        cve_info_dict.update({"Vulnerability Exist Time": None, "Linux Kernel Version Number": None})
    if not cve_info_dict['Linux Kernel Version Number']:
        return {}

    content = Repository.requests_get_content(cve_info_url, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if not content:
        return {}
    soup = bs4.BeautifulSoup(content, 'lxml')
    cve_info_dict.update({'Vulnerability Type': get_vulnerability_type(soup)})
    cve_info_dict.update({"CVSS Severity V2": get_cvss_v2_base_score_and_vector_dict(soup)})
    cve_info_dict.update({'Vulnerability Discover Time': get_vuln_discover_time(soup)})
    if cve_info_dict['Vulnerability Discover Time'] and cve_info_dict['Vulnerability Exist Time']:
        cve_info_dict.update(
            {'Interval Between Exist And Discover': (cve_info_dict['Vulnerability Discover Time']
                                                     - cve_info_dict['Vulnerability Exist Time']).days})
    else:
        cve_info_dict.update({'Interval Between Exist And Discover': None})
    return cve_info_dict


def save_linux_kernel_character_factor(save_dir, row_index, beginning_start_index):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    key_word = 'linux+kernel'
    cve_count = Repository.get_cve_count(key_word)
    if not cve_count or cve_count <= 0:
        return False

    save_path = os.path.join(save_dir, 'Linux Kernel Character Factor.xls')
    init_workbook(save_path)
    count = beginning_start_index + 1

    for start_index in range(beginning_start_index, cve_count, 20):
        search_result_url = 'https://nvd.nist.gov/vuln/search/results' \
                            '?form_type=Basic&results_type=overview' \
                            '&query=' + key_word + '&search_type=all&startIndex=' + str(start_index)
        print("\rConnect:" + search_result_url, end='')

        cve_id_list = Repository.get_cve_id_list(search_result_url)
        if not cve_id_list:
            print("\r\033[1;31mNo CVE:" + search_result_url + '\033[0m')
            count += 20
            continue
        for cve_id in cve_id_list:
            cve_info_url = "https://nvd.nist.gov/vuln/detail/" + cve_id
            print("\rConnect:" + cve_info_url + '\tCount:' + str(count) + '\tRate:' + str(
                int(count / cve_count * 100)) + '%', end='')
            cve_info_dict = get_cve_info_dict(cve_info_url)
            cve_info_dict.update({'CVE Number': cve_id})
            if write_workbook(cve_info_dict, save_path, row_index):
                row_index += 1
            count += 1
    return True


def get_vulnerability_type(soup):
    for tag_li in soup.select('div.technicalDetails ul li'):
        return tag_li.get_text().strip()
    return None


def get_cve_publish_date(soup):
    for tag_dd in soup.select('span[data-testid=vuln-published-on]'):
        publish_date = None
        try:
            publish_date = datetime.datetime.strptime(tag_dd.get_text().strip(), "%m/%d/%Y")
        except (TypeError, ValueError):
            pass
        return publish_date
    return None


def get_vuln_discover_time_in_github(hyperlink):
    content = Repository.requests_get_content(hyperlink, timeout=6,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        discover_time = None
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_relative_time in soup.select('relative-time'):
            try:
                discover_time = datetime.datetime.strptime(tag_relative_time['datetime'],
                                                           "%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, TypeError):
                try:
                    discover_time = datetime.datetime.strptime(tag_relative_time.get_text().strip(),
                                                               "%b %d, %Y")
                except ValueError:
                    pass
        return discover_time
    return None


def get_vuln_discover_time_in_patchwork(hyperlink):
    content = Repository.requests_get_content(hyperlink, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        discover_time = None
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_tr in soup.select('table.patchmeta tr'):
            if re.match(r'Date', tag_tr.find('th').get_text().strip(), re.I):
                for tag_td in tag_tr.select('td'):
                    match = re.match(r'\w+ \d+, \d+', tag_td.get_text().strip())
                    if match:
                        try:
                            discover_time = datetime.datetime.strptime(match.group(), "%B %d, %Y")
                        except ValueError:
                            pass
        return discover_time
    return None


def get_vuln_discover_time_in_git(hyperlink):
    content = Repository.requests_get_content(hyperlink, timeout=10,
                                              headers={
                                                  'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        discover_time = None
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_tr in soup.select('table.commit-info tr'):
            if re.match(r'author', tag_tr.find('th').get_text().strip(), re.I):
                for tag_td in tag_tr.select('td.right'):
                    match = re.match(r'\d+-\d+-\d+', tag_td.get_text().strip())
                    if match:
                        try:
                            discover_time = datetime.datetime.strptime(match.group(), "%Y-%m-%d")
                        except ValueError:
                            pass
        return discover_time
    return None


if __name__ == "__main__":
    oldest_linux_kernel_version_number = '1.2.0'
    latest_linux_kernel_version_number = '4.14'
    g_linux_kernel_release_time_file_path = r'C:\Users\79196\Downloads\NVD\Linux Kernel Release Time.xls'
    save_linux_kernel_character_factor(r'C:\Users\79196\Downloads\NVD', row_index=1353,
                                       beginning_start_index=1874)
