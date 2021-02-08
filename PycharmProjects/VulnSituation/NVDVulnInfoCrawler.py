# Author: 14281055 Liheng Chen CIT BJTU
# File Name: NVDVulnInfoCrawler.py

import re
import os
import bs4
import xlrd
import xlwt
from xlutils.copy import copy
import Repository


def write_workbook(vuln_detail_dict, save_path, row):
    r_workbook = xlrd.open_workbook(save_path, formatting_info=True)
    w_workbook = copy(r_workbook)
    w_sheet = w_workbook.get_sheet(0)

    keys = ['CVE Number', 'Current Description', 'Analysis Description', 'Vulnerability Type']
    cvss_v3_keys = ['CVSS v3 Base Score', 'Vector', 'Impact Score', 'Exploitability Score']
    cvss_v2_keys = ['CVSS v2 Base Score', 'Vector', 'Impact Subscore', 'Exploitability Subscore']
    reference_keys = ['Hyperlink', 'Resource']

    start_col = 0
    for key in keys:
        if key in vuln_detail_dict.keys():
            w_sheet.write(row, start_col, vuln_detail_dict[key])
        start_col += 1

    if 'CVSS Severity V3' in vuln_detail_dict.keys():
        cvss_v3_dict = vuln_detail_dict['CVSS Severity V3']
        for key in cvss_v3_keys:
            if key in cvss_v3_dict.keys():
                w_sheet.write(row, start_col, cvss_v3_dict[key])
            elif key is 'Impact Score' and 'Impact Subscore' in cvss_v3_dict.keys():
                w_sheet.write(row, start_col, cvss_v3_dict['Impact Subscore'])
            elif key is 'Exploitability Score' and 'Exploitability Subscore' in cvss_v3_dict.keys():
                w_sheet.write(row, start_col, cvss_v3_dict['Exploitability Subscore'])
            start_col += 1

    if 'CVSS Severity V2' in vuln_detail_dict.keys():
        cvss_v2_dict = vuln_detail_dict['CVSS Severity V2']
        for key in cvss_v2_keys:
            if key in cvss_v2_dict.keys():
                w_sheet.write(row, start_col, cvss_v2_dict[key])
            elif key is 'Impact Subscore' and 'Impact Score' in cvss_v2_dict.keys():
                w_sheet.write(row, start_col, cvss_v2_dict['Impact Score'])
            elif key is 'Exploitability Subscore' and 'Exploitability Score' in cvss_v2_dict.keys():
                w_sheet.write(row, start_col, cvss_v2_dict['Exploitability Score'])
            start_col += 1

    if 'References' in vuln_detail_dict.keys():
        reference_list = vuln_detail_dict['References']
        count = 1
        for reference in reference_list:
            if 'Resource' in reference.keys() and re.match('.*patch', reference['Resource'], re.I):
                color_index = 2
            else:
                color_index = 0
            for key in reference_keys:
                if key in reference.keys():
                    w_sheet.write(row, start_col, reference[key],
                                  Repository.set_font(color_index=color_index))
                start_col += 1
            if count == 25:
                break
            count += 1

    w_workbook.save(save_path)


def init_workbook(path):
    # Judge path exists or not
    if os.path.exists(path):
        os.remove(path)
    # Open workbook
    w_workbook = xlwt.Workbook()
    w_sheet = w_workbook.add_sheet('NVD Vuln Detail', cell_overwrite_ok=True)

    # Table head
    heads = ['CVE Number', 'Current Description', 'Analysis Description', 'Vulnerability Type']
    cvss_head = ['Base Score', 'Vector', 'Impact Score', 'Exploitability Score']
    reference_head = ['Hyperlink', 'Resource']

    # Write Head
    start_col = 0
    cell_width = w_sheet.col(0).width
    # Write heads
    for col in range(start_col, start_col + len(heads)):
        w_sheet.write_merge(0, 1, col, col, heads[col - start_col], Repository.set_font(bold=True))
        w_sheet.col(col).width = int(cell_width * 1.75)
    start_col += len(heads)
    # Write CVSS V3 head
    w_sheet.write_merge(
        0, 0,
        start_col, start_col + len(cvss_head) - 1,
        'CVSS Severity V3', Repository.set_font(bold=True)
    )
    for col in range(start_col, start_col + len(cvss_head)):
        w_sheet.write(1, col, cvss_head[col - start_col], Repository.set_font(bold=True))
        w_sheet.col(col).width = int(cell_width * 1.25)
    start_col += len(cvss_head)
    # Write CVSS V2 head
    w_sheet.write_merge(
        0, 0,
        start_col, start_col + len(cvss_head) - 1,
        'CVSS Severity V2', Repository.set_font(bold=True)
    )
    for col in range(start_col, start_col + len(cvss_head)):
        w_sheet.write(1, col, cvss_head[col - start_col], Repository.set_font(bold=True))
        w_sheet.col(col).width = int(cell_width * 1.25)
    start_col += len(cvss_head)
    # Write reference head
    for index in range(0, 25):
        reference_title = 'Reference ' + str(index + 1)
        w_sheet.write_merge(
            0, 0,
            start_col, start_col + len(reference_head) - 1,
            reference_title, Repository.set_font(bold=True)
        )
        for col in range(start_col, start_col + len(reference_head)):
            w_sheet.write(1, col, reference_head[col - start_col], Repository.set_font(bold=True))
            w_sheet.col(col).width = int(cell_width * 2)
        start_col += len(reference_head)

    # Save
    w_workbook.save(path)


def get_dl_dict(base_soup, attrs=None):
    if attrs is None:
        attrs = {}
    dl_dict = {}
    tag_dl = base_soup.find('dl', attrs=attrs)
    if tag_dl:
        keys = []
        for tag_dt in tag_dl.find_all('dt'):
            keys.append(tag_dt.get_text().strip().replace(':', ''))
        values = []
        for tag_dd in tag_dl.find_all('dd'):
            values.append(tag_dd.get_text().strip())

        for index in range(len(keys)):
            if index < len(values):
                dl_dict.update({keys[index]: values[index]})
            else:
                dl_dict.update({keys[index]: ''})
    return dl_dict


def update_dict_with_soup(dictionary, key, soup):
    if key is not '':
        if soup:
            dictionary.update({key: soup.get_text().strip()})
        else:
            dictionary.update({key: ''})


# Capture vuln detail
def get_vuln_detail_dict(vuln_detail_url):
    vuln_detail_dict = {}
    # Connect
    content = Repository.requests_get_content(vuln_detail_url, try_times=5, timeout=5)
    if not content:
        return vuln_detail_dict
    url_soup = bs4.BeautifulSoup(content, "html.parser")
    # Add current description
    update_dict_with_soup(vuln_detail_dict, 'Current Description',
                          url_soup.find('p', attrs={'data-testid': 'vuln-description'}))
    # Add analysis description
    update_dict_with_soup(vuln_detail_dict, 'Analysis Description',
                          url_soup.find('p', attrs={'data-testid': 'vuln-analysis-description'}))
    # Add impact
    vuln_detail_dict.update(
        {"CVSS Severity V3": get_dl_dict(url_soup, {'data-testid': 'vuln-cvssv3-score-container'})})
    vuln_detail_dict.update(
        {"CVSS Severity V2": get_dl_dict(url_soup, {'data-testid': 'vuln-cvssv2-score-container'})})
    # Add reference
    reference_list = Repository.get_reference_dict_list(url_soup)
    patch_list = []
    for reference in reference_list:
        if re.match('.*patch', reference['Resource'], re.I):
            reference_list.remove(reference)
            patch_list.append(reference)
    patch_list.extend(reference_list)
    vuln_detail_dict.update({'References': patch_list})
    # Add vuln type
    tag_div = url_soup.find('div', attrs={'class': 'technicalDetails'})
    if tag_div:
        tag_li = tag_div.find('li')
        if tag_li:
            vuln_detail_dict.update({'Vulnerability Type': tag_li.get_text().strip()})

    return vuln_detail_dict


# Write vuln detail in excel
def write_oss_vuln_detail(oss_info_dict):
    # Get NVD records count
    if 'Key Word' not in oss_info_dict.keys():
        return
    key_word = oss_info_dict['Key Word'].strip().replace(" ", "+")
    oss_info_dict.update({'NVD Records Count': Repository.get_cve_count(key_word)})
    print("NVD Records Count:" + str(oss_info_dict['NVD Records Count']))
    if oss_info_dict['NVD Records Count'] <= 0:
        return
    # init workbook
    save_path = \
        'C:/Users/79196/Downloads/NVD/Simpler Result/' + oss_info_dict['Sequence Number'] \
        + '-' + oss_info_dict['Key Word'] + '.xls'
    init_workbook(save_path)
    row = 2
    # Make Search Result URL
    for start_index in range(0, oss_info_dict['NVD Records Count'], 20):
        search_result_url = "https://nvd.nist.gov/vuln/search/results" \
                            "?adv_search=false&form_type=basic" \
                            "&results_type=overview&search_type=all" \
                            "&query=" + key_word + "&startIndex=" + str(start_index)
        print("Connect:" + search_result_url)

        # Capture vuln ID in one page
        cve_id_list = Repository.get_cve_id_list(search_result_url)
        if not cve_id_list:
            print("No CVE Entry:" + search_result_url)

        # Write vuln detail
        for cve_id in cve_id_list:
            cve_detail_url = "https://nvd.nist.gov/vuln/detail/" + cve_id
            print("Connect:" + cve_detail_url, end='\t\t')
            # Get vuln detail
            vuln_detail_dict = get_vuln_detail_dict(cve_detail_url)
            vuln_detail_dict.update({'CVE Number': cve_id})
            vuln_detail_dict.update({'Detail Link': cve_detail_url})
            write_workbook(vuln_detail_dict, save_path, row)
            print('Rate:' + str(int((row - 1) / oss_info_dict['NVD Records Count'] * 100)) + '%')
            row += 1


# Entrance
def main():
    save_dir = 'C:/Users/79196/Downloads/NVD/Result'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # Get software name
    print("Getting software name...")
    software_name_list_path = "C:/Users/79196/Downloads/NVD/OSSList(V2).xls"
    r_workbook = xlrd.open_workbook(software_name_list_path)
    for r_sheet in r_workbook.sheets():
        if r_sheet.nrows > 1:
            for row in range(1, r_sheet.nrows):
                oss_info_dict = {
                    'Sequence Number': str(r_sheet.cell(row, 0).value.strip()),
                    'Name': str(r_sheet.cell(row, 1).value.strip()),
                    'Key Word': str(r_sheet.cell(row, 2).value.strip()),
                    'Describe': str(r_sheet.cell(row, 3).value.strip())
                }
                print("Sequence Number:" + oss_info_dict['Sequence Number']
                      + "\nSoftware:" + oss_info_dict['Name'])
                # Write vuln detail
                write_oss_vuln_detail(oss_info_dict)


if __name__ == "__main__":
    main()
