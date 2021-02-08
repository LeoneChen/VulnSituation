# 作者信息：陈力恒 北京交通大学 安全1402 14281055
# 文件名：  CNVDCrawler.py

# 内建模块
import os

# 网页访问与分析（扩展模块）
import requests
import bs4

# Excel模块（扩展模块）
import xlrd
import xlwt
from xlutils.copy import copy


def get_patch_vuln_detail(
        referer_url, detail_url, detail_url_open_error_list, detail_url_analyse_error_list):
    # 构造空的详情条目字典
    detail_entry_dict = {}

    # 打开详情网页
    print("打开详情网页：" + detail_url)
    search_result_url_response = try_requests_get(referer_url, detail_url, 5, 5)
    if search_result_url_response is None:
        detail_url_open_error_list.append(detail_url)
        return detail_entry_dict
    else:
        detail_url_content = search_result_url_response.content

    # 分析详情网页
    detail_url_content_soup = bs4.BeautifulSoup(detail_url_content, "html.parser")

    # 捕获标题
    tag_h1 = detail_url_content_soup.find('h1')
    if tag_h1 is not None:
        detail_entry_dict["标题"] = tag_h1.get_text().strip()

    # 捕获详情条目
    tag_table = detail_url_content_soup.find('table', attrs={'class', 'gg_detail'})
    if tag_table is not None:
        tag_tbody = tag_table.find('tbody')
        if tag_tbody is not None:
            for tag_tr in tag_tbody.find_all('tr'):
                tag_td_list = tag_tr.find_all('td')
                if 2 == len(tag_td_list):
                    detail_entry_dict[tag_td_list[0].get_text().strip()] = \
                        tag_td_list[1].get_text().strip()

    # 判断详情条目是否为空
    if not detail_entry_dict:
        detail_url_analyse_error_list.append(detail_url)
        print("详情条目为空：" + detail_url)

    return detail_entry_dict


def try_requests_get(referer_url, url, timeout=0.01, try_times=3):
    __jsluid = 'e3cec0ef4a49b76cab953e7d4efebc88'
    __jsl_clearance = '1516078445.917|0|1C8HVwyczdF%2Bzs5NO0VJ7uhm3nU%3D'
    JSESSIONID = '086A2720933744698DDE25024727570D'
    bdshare_firstime = '1515917061738'
    Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa = '1516033186'
    headers = {
        'Host': 'www.cnvd.org.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': referer_url,
        'Cookie': '__jsluid=' + __jsluid
                  + '; __jsl_clearance=' + __jsl_clearance
                  + '; JSESSIONID=' + JSESSIONID
                  + '; bdshare_firstime=' + bdshare_firstime
                  + '; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=' + Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa,
        'Connection': 'keep-alive',
        # 'Upgrade-Insecure-Requests': '1',
        # 'Cache-Control': 'max-age=0',
    }
    cookies = {'__jsluid': __jsluid,
               '__jsl_clearance': __jsl_clearance,
               'JSESSIONID': JSESSIONID,
               'bdshare_firstime': bdshare_firstime}

    try_times_temp = try_times
    while try_times_temp > 0:
        try:
            url_response = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
            if url_response.status_code != 200:
                print("响应代码:" + str(url_response.status_code))
                try_times_temp -= 1
                continue
            if url_response.text is '':
                print("请求为空！")
                try_times_temp -= 1
                continue
        except requests.exceptions.ReadTimeout:
            try_times_temp -= 1
        except requests.exceptions.ConnectionError:
            try_times_temp -= 1
        else:
            break
    else:
        print(str(try_times) + "次连接均失败：" + url)
        return None
    return url_response


def get_patch_detail_url_list(search_result_url):
    # 构造空的补丁详情链接列表
    patch_detail_url_list = []

    # 打开查询结果网页
    print("打开查询结果网页：" + search_result_url)
    search_result_url_response = try_requests_get(
        'http://www.cnvd.org.cn/patchInfo'
        '/list?startDate=&patchName=firefox&endDate='
        '&%E6%8F%90%E4%BA%A4=%E6%8F%90%E4%BA%A4&max=20&offset=0',
        search_result_url, 5, 5)
    if search_result_url_response is None:
        patch_detail_url_open_error_list.append(search_result_url)
        return patch_detail_url_list
    else:
        search_result_url_content = search_result_url_response.content

    # 分析查询结果网页
    search_result_url_content_soup = bs4.BeautifulSoup(search_result_url_content, "html.parser")
    tag_tbody = search_result_url_content_soup.find('table', attrs={'class', 'tlist'}).find('tbody')
    if tag_tbody is not None:
        for tag_tr in tag_tbody.find_all('tr'):
            for tag_a in tag_tr.find_all('a'):
                if tag_a.get('href') is not '':
                    patch_detail_url_list.append(tag_a.get('href'))

    # 判断补丁详情链接列表是否为空
    if not patch_detail_url_list:
        print("补丁详情链接为空：" + search_result_url)
        patch_detail_url_analyse_error_list.append(search_result_url)

    return patch_detail_url_list


def get_vuln_patch_detail_entry(referer_url, patch_detail_url):
    # 获取补丁详情
    print("获取补丁详情：" + patch_detail_url)
    patch_detail_entry_dict = get_patch_vuln_detail(referer_url,
                                                    patch_detail_url,
                                                    patch_detail_url_open_error_list,
                                                    patch_detail_url_analyse_error_list)

    patch_detail_entry_dict['补丁详情链接'] = patch_detail_url

    # 判断补丁详情是否为空
    if not patch_detail_entry_dict:
        return patch_detail_entry_dict

    # 修改“标题”为“补丁标题”
    if '标题' in patch_detail_entry_dict.keys():
        patch_detail_entry_dict['补丁标题'] = patch_detail_entry_dict.pop('标题')

    # 判断是否有所属漏洞编号
    if '所属漏洞编号' not in patch_detail_entry_dict.keys():
        return patch_detail_entry_dict

    # 获取漏洞详情
    vuln_detail_url = "http://www.cnvd.org.cn/flaw/show/" + patch_detail_entry_dict["所属漏洞编号"]
    vuln_detail_entry_dict = get_patch_vuln_detail(patch_detail_url,
                                                   vuln_detail_url,
                                                   vuln_detail_url_open_error_list,
                                                   vuln_detail_url_analyse_error_list)

    vuln_detail_entry_dict['漏洞详情链接'] = vuln_detail_url

    # 判断漏洞详情是否为空
    if not vuln_detail_entry_dict:
        return patch_detail_entry_dict

    # 修改“标题”为“漏洞标题”
    if '标题' in vuln_detail_entry_dict.keys():
        vuln_detail_entry_dict['漏洞标题'] = vuln_detail_entry_dict.pop('标题')

    # 合并两个字典
    patch_detail_entry_dict.update(vuln_detail_entry_dict)

    return patch_detail_entry_dict


def init_workbook(path):
    # 判断Excel文件是否存在
    if not os.path.exists(path):

        # 打开工作簿，添加工作表
        w_workbook = xlwt.Workbook()
        w_sheet = w_workbook.add_sheet('CNVD漏洞', cell_overwrite_ok=True)

        # 工作表的表头
        row_head = ['补丁详情链接', '补丁标题', '所属漏洞编号', '补丁链接', '补丁描述', '补丁附件',
                    '补丁状态', '补丁审核意见', '漏洞详情链接', '漏洞标题', 'CNVD-ID', '公开日期',
                    '影响产品', 'BUGTRAQ ID', 'CVE ID', '漏洞描述', '参考链接', '漏洞解决方案',
                    '厂商补丁', '验证信息', '报送时间', '收录时间', '更新时间', '漏洞附件']

        # 设置字体样式
        cell_font = xlwt.Font()
        cell_font.bold = True
        cell_style = xlwt.XFStyle()
        cell_style.font = cell_font

        # 写入表头
        for ncols in range(0, len(row_head)):
            w_sheet.write(0, ncols, row_head[ncols], cell_style)

        # 保存工作簿
        w_workbook.save(path)


def save_error():
    # Error路径
    error_root_dir = "C:\\CNVD\\Error"

    # 写入Search Result Url Error
    write_error(error_root_dir + "\\Search Result Url", search_result_url_open_error_list,
                search_result_url_analyse_error_list)

    # 写入Patch Detail Url Error
    write_error(error_root_dir + "\\Patch Detail Url", patch_detail_url_open_error_list,
                patch_detail_url_analyse_error_list)

    # 写入Vuln Detail Url Error
    write_error(error_root_dir + "\\Vuln Detail Url", vuln_detail_url_open_error_list,
                vuln_detail_url_analyse_error_list)


def write_error(save_dir, open_error_list, analyse_error_list):
    # 创建文件夹
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 写入Open Error.txt文件
    write_error_list_by_path(save_dir + "\\Open Error.txt", open_error_list)

    # 写入Analyse Error.txt文件
    write_error_list_by_path(save_dir + "\\Analyse Error.txt", analyse_error_list)


def write_error_list_by_path(save_path, error_list):
    # 打开文件
    try:
        error_file = open(save_path, 'w', encoding='utf-8')
    except IOError:
        print("文件打开失败：" + save_path)
        return False

    # 将列表写入文件
    for error_list_index in range(len(error_list)):
        error_file.write(error_list[error_list_index])
        error_file.write('\n')

    error_file.close()
    return True


def main():
    # 输入查询关键字
    if debug:
        query_key_word = "firefox"
    else:
        while True:
            query_key_word = input('Key Word:').strip().replace(" ", "+")
            if "" != query_key_word:
                break

    # 输入起始偏移量
    if debug:
        beginning_offset = 5
    else:
        while True:
            beginning_offset = int(input("Beginning Offset:"))
            if beginning_offset >= 0:
                break

    # Excel保存路径
    save_dir = "C:\\CNVD"
    save_path = save_dir + "\\CNVD.xls"

    # 创建文件夹
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 判断工作簿是否存在
    if os.path.exists(save_path):
        os.remove(save_path)

    init_workbook(save_path)

    r_workbook = xlrd.open_workbook(save_path, formatting_info=True)
    w_workbook = copy(r_workbook)
    r_worksheet = r_workbook.sheet_by_index(0)
    w_worksheet = w_workbook.get_sheet(0)

    ncols = r_worksheet.ncols
    row = beginning_offset + 1

    # 构造查询结果的网页链接
    search_result_url = "http://www.cnvd.org.cn/patchInfo/list?startDate=&patchName=" \
                        + query_key_word \
                        + "&endDate=&%E6%8F%90%E4%BA%A4=%E6%8F%90%E4%BA%A4&max=20&offset=" \
                        + str(beginning_offset)

    # 捕获一页中的补丁详情的链接
    patch_detail_url_list = get_patch_detail_url_list(search_result_url)

    if lazy:
        patch_detail_url_list = ['/patchInfo/show/105285']
    # 捕获补丁详情
    for patch_detail_url in patch_detail_url_list:
        detail_entry_dict = get_vuln_patch_detail_entry(search_result_url,
                                                        "http://www.cnvd.org.cn" + patch_detail_url)
        if detail_entry_dict:
            for col in range(ncols):
                if r_worksheet.cell(0, col).value in detail_entry_dict.keys():
                    w_worksheet.write(row, col, detail_entry_dict[r_worksheet.cell(0, col).value])
                else:
                    w_worksheet.write(row, col, "无")
            print('写入第' + str(row) + '条')
            w_workbook.save(save_path)
            if 0 == row % 5:
                exit(1)
            row += 1

    save_error()


# 函数入口
if __name__ == "__main__":
    debug = True
    lazy = False

    search_result_url_open_error_list = []
    patch_detail_url_open_error_list = []
    vuln_detail_url_open_error_list = []

    search_result_url_analyse_error_list = []
    patch_detail_url_analyse_error_list = []
    vuln_detail_url_analyse_error_list = []

    main()
