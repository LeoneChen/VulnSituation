# Author: 14281055 Liheng Chen CIT BJTU
# File Name: CVECountByYearStatistics.py

import os
import bs4
import xlrd
import xlsxwriter
import Repository
import random


def write_cve_count_statistics(oss_info_dict, save_dir_path):
    # Get NVD records count
    if 'Key Word' not in oss_info_dict.keys():
        return False
    # Path
    save_path = os.path.join(
        save_dir_path, oss_info_dict['Number'] + '-' + oss_info_dict['Key Word'] + '.xls')
    # Open workbook
    w_workbook = xlsxwriter.Workbook(save_path)
    w_sheet = w_workbook.add_worksheet('Statistics')

    # Table head
    heads = ['Year', 'Matches', 'Total', 'Percentage']

    # Write Head
    w_sheet.write_column('A1', heads, w_workbook.add_format({'bold': 'True'}))

    # Make Statistics URL
    statistics_url = 'https://nvd.nist.gov/vuln/search/statistics' \
                     '?form_type=Basic&results_type=statistics' \
                     '&query=' + Repository.padding(oss_info_dict['Key Word']) + '&search_type=all'
    print("Connect:" + statistics_url)
    content = Repository.requests_get_content(statistics_url, timeout=5, headers={
        'User-Agent': random.choice(Repository.user_agent_list)})
    if content:
        soup = bs4.BeautifulSoup(content, 'lxml')
        for tag_tbody in soup.select('table.table.table-striped.table-hover tbody'):
            col_index = 1
            for tag_tr in tag_tbody.find_all('tr'):
                tag_th = tag_tr.find('th')
                if tag_th:
                    w_sheet.write(0, col_index, int(tag_th.get_text().strip()))
                row_index = 1
                for tag_td in tag_tr.find_all('td'):
                    if row_index == 3:
                        cell_format = w_workbook.add_format()
                        cell_format.set_num_format('0.00%')
                        cell_value = float(tag_td.get_text().strip().replace('%', '')) / 100
                        w_sheet.write(row_index, col_index, cell_value, cell_format)
                    else:
                        w_sheet.write(row_index, col_index, int(tag_td.get_text().strip().replace(',', '')))
                    row_index += 1
                col_index += 1
            column_chart = w_workbook.add_chart({'type': 'column'})

            column_chart.add_series({
                'categories': ['Statistics', 0, 1, 0, col_index - 1],
                'values': ['Statistics', 1, 1, 1, col_index - 1],
                'name': ['Statistics', 1, 0]
            })
            column_chart.set_size({'width': 500, 'height': 300})
            column_chart.set_title({'name': 'Total Matches By Year'})
            column_chart.set_x_axis({'name': 'Year'})
            column_chart.set_y_axis({'name': '# of Vulnerabilities Meeting Specified Limitation'})
            w_sheet.insert_chart('A6', column_chart)

            column_chart = w_workbook.add_chart({'type': 'column'})
            column_chart.add_series({
                'categories': ['Statistics', 0, 1, 0, col_index - 1],
                'values': ['Statistics', 3, 1, 3, col_index - 1],
                'name': ['Statistics', 3, 0]
            })
            column_chart.set_size({'width': 500, 'height': 300})
            column_chart.set_title({'name': 'Percent Matches By Year'})
            column_chart.set_x_axis({'name': 'Year'})
            column_chart.set_y_axis({'name': '% of Vulnerabilities Meeting Specified Limitation'})
            w_sheet.insert_chart('I6', column_chart)

    # Save
    w_workbook.close()


def cve_count_by_year_statistics(save_dir_path, oss_list_path):
    if not os.path.exists(save_dir_path):
        os.makedirs(save_dir_path)
    # Get software name
    r_workbook = xlrd.open_workbook(oss_list_path)
    for r_sheet in r_workbook.sheets():
        if r_sheet.nrows > 1:
            for row in range(1, r_sheet.nrows):
                oss_info_dict = {
                    'Number': str(r_sheet.cell(row, 0).value.strip()),
                    'Name': str(r_sheet.cell(row, 1).value.strip()),
                    'Key Word': str(r_sheet.cell(row, 2).value.strip()),
                    'Description': str(r_sheet.cell(row, 3).value.strip())
                }
                print("Number:" + oss_info_dict['Number']
                      + "\nName:" + oss_info_dict['Name'])
                # Write vuln statistics
                write_cve_count_statistics(oss_info_dict, save_dir_path)


if __name__ == '__main__':
    cve_count_by_year_statistics(r'C:\Users\79196\Downloads\NVD\Statistics',
                                 r'C:\Users\79196\Downloads\NVD\OSSList(V2).xls')
