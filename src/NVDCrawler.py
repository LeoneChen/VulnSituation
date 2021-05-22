# Author: 14281055 Liheng Chen CIT BJTU
# File Name: NVDVulnInfoCrawler.py

import re
import os
import bs4
import xlrd
import xlwt
from xlutils.copy import copy
import VulnSituation.Repository

# Worksheet Table Head
heads = ['CVE ID', 'Current Description', 'CVSSv3 Score', 'CVSSv2 Score']
reference_head = ['Hyperlink', 'Resource']
max_reference_nr = 10


def write_workbook(cve_detail, save_path, row):
    r_workbook = xlrd.open_workbook(save_path, formatting_info=True)
    w_workbook = copy(r_workbook)
    w_sheet = w_workbook.get_sheet(0)

    start_col = 0
    for key in heads:
        if key in cve_detail.keys():
            w_sheet.write(row, start_col, cve_detail[key])
        start_col += 1

    if 'References' in cve_detail.keys():
        references = cve_detail['References']
        count = 1
        for reference in references:
            color_index = \
                2 if 'Resource' in reference.keys() and re.match('.*patch', reference['Resource'], re.I) else 0
            for key in reference_head:
                if key in reference.keys():
                    w_sheet.write(row, start_col, reference[key],
                                  VulnSituation.Repository.set_font(color_index=color_index))
                start_col += 1
            if count == max_reference_nr:
                break
            count += 1

    w_workbook.save(save_path)


def init_workbook_head(path):
    # Judge path exists or not
    if os.path.exists(path):
        os.remove(path)
    # Open workbook
    w_workbook = xlwt.Workbook()
    w_sheet = w_workbook.add_sheet('CVE Detail', cell_overwrite_ok=True)

    # Write Head
    start_col = 0
    cell_width = w_sheet.col(0).width

    # Write heads
    for col in range(start_col, start_col + len(heads)):
        w_sheet.write_merge(0, 1, col, col, heads[col - start_col], VulnSituation.Repository.set_font(bold=True))
        w_sheet.col(col).width = int(cell_width * 1.75)
    start_col += len(heads)

    # Write reference head
    for index in range(0, max_reference_nr):
        reference_title = 'Reference ' + str(index + 1)
        w_sheet.write_merge(
            0, 0,
            start_col, start_col + len(reference_head) - 1,
            reference_title, VulnSituation.Repository.set_font(bold=True)
        )
        for col in range(start_col, start_col + len(reference_head)):
            w_sheet.write(1, col, reference_head[col - start_col], VulnSituation.Repository.set_font(bold=True))
            w_sheet.col(col).width = int(cell_width * 2)
        start_col += len(reference_head)

    # Save
    w_workbook.save(path)


# get cve detail
def get_cve_detail(cve_detail_url):
    cve_detail = {}
    # Connect
    response = VulnSituation.Repository.requests_get(cve_detail_url, try_times=5, timeout=5)
    if not response:
        return {}
    else:
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        response.close()

    cve_detail.update(
        {'Current Description': bs.select('p[data-testid=vuln-description]')[0].get_text().strip()}
    )
    cve_detail.update(
        {"CVSSv3 Score": bs.select('span[class=severityDetail]')[
            0].get_text().strip()}
    )
    # cve_detail.update(
    #     {"CVSSv3 Vector": bs.select('span[data-testid=vuln-cvss3-nist-vector]')[0].get_text().strip()}
    # )
    cve_detail.update(
        {"CVSSv2 Score": bs.select('span a[id=Cvss2CalculatorAnchor]')[0].get_text().strip()}
    )
    # cve_detail.update(
    #     {"CVSSv2 Vector": bs.select('span[data-testid=vuln-cvss2-panel-vector]')[0].get_text().strip()}
    # )
    # Add reference
    references = VulnSituation.Repository.get_references(bs)
    patchs = []
    for reference in references:
        if re.match('.*patch', reference['Resource'], re.I):
            references.remove(reference)
            patchs.append(reference)
    patchs.extend(references)
    cve_detail.update({'References': patchs})
    # Add cwe
    cve_detail.update({'CWE': bs.select('td[data-testid*=vuln-CWEs-link-]')[0].get_text().strip()})

    return cve_detail


# save CVEs detail in excel
def save_cve_detail(key_word, output_dir):
    # Get nr of cves related to key_word
    cve_count = VulnSituation.Repository.get_cve_count(key_word)
    # cve_count = 1
    print("[" + key_word + "] CVE Count:" + str(cve_count))
    if cve_count <= 0:
        return
    # init workbook
    save_path = os.path.join(output_dir, key_word + '.xls')
    init_workbook_head(save_path)
    cur_row = 2  # start from row 2

    # Make Search Result URL
    for start_index in range(0, cve_count, 20):
        # e.g. https://nvd.nist.gov/vuln/search/results?query=Memcached&results_type=overview&form_type=Basic&search_type=all&startIndex=20
        search_result_url = "https://nvd.nist.gov/vuln/search/results" \
                            "?form_type=Basic&results_type=overview&search_type=all" \
                            "&query=" + key_word + "&startIndex=" + str(start_index)
        print("Connect: " + search_result_url)

        # get CVEID in one result page
        cve_id_list = VulnSituation.Repository.get_cve_id_list(search_result_url)
        # cve_id_list = ["CVE-2014-6283"]
        if not cve_id_list:
            print("No CVE:" + search_result_url)

        # Write cve detail
        for cve_id in cve_id_list:
            cve_detail_url = "https://nvd.nist.gov/vuln/detail/" + cve_id
            print("Connect: " + cve_detail_url, end='\t\t')

            # Get cve detail
            cve_detail = get_cve_detail(cve_detail_url)
            cve_detail.update({'CVE ID': cve_id})
            cve_detail.update({'Detail Link': cve_detail_url})
            write_workbook(cve_detail, save_path, cur_row)
            print('Rate:' + str(int((cur_row - 1) / cve_count * 100)) + '%')
            cur_row += 1


# main func
def NVDCrawler(key_word):
    output_dir = '../output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    save_cve_detail(key_word, output_dir)


if __name__ == "__main__":
    NVDCrawler("sgx")
