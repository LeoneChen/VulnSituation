import re
import os
import requests
import bs4

debug = True
lazy = False


def get_vulnerability_code(internal_vulnerability_detail_url, internal_vulnerability_id):
    # 判断CVE编号漏洞文件夹是否存在
    save_path = "C:\\CVE\\" + internal_vulnerability_id
    print(save_path)
    if os.path.exists(save_path):
        print("Exists")
        return 0

    url_text = requests.get(internal_vulnerability_detail_url).text
    # 利用正则查找所有连接
    patch_url_list = re.findall(
        r"https?://git\.kernel\.org/cgit/linux/kernel/git/torvalds/linux\.git/commit/"
        r"\?id=[0-9]+[a-zA-Z]+[0-9a-zA-Z]*",
        url_text)

    if len(patch_url_list) < 1:
        patch_url_list = re.findall(
            r"https?://git\.kernel\.org/cgit/linux/kernel/git/torvalds/linux\.git/commit/"
            r"\?id=[a-zA-Z]+[0-9]+[0-9a-zA-Z]*",
            url_text)
        if len(patch_url_list) < 1:
            print("无链接！")
            return 0

    vulnerability_patch_row_list = []
    code_url_list = []
    vulnerability_previous_code_list = []
    vulnerability_post_code_list = []

    print(patch_url_list[0])
    patch_url_content = requests.get(patch_url_list[0]).content
    patch_url_content_soup = bs4.BeautifulSoup(patch_url_content, "html.parser")

    # 创建以cve编号为文件夹名的文件夹
    os.makedirs(save_path)

    # 漏洞文件名字
    for tag_td in patch_url_content_soup.find_all('td', attrs={'class', 'upd'}):
        for tag_a in tag_td.find_all('a'):
            vulnerability_name = tag_a.get_text()
            vulnerability_patch_row_list.append(vulnerability_name)

    # 漏洞补丁代码
    for tag_td in patch_url_content_soup.find_all('table', attrs={'class', 'diff'}):
        for tag_div in tag_td.find_all('div'):
            vulnerability_code = tag_div.get_text()
            vulnerability_patch_row_list.append(vulnerability_code)

    # 存入patch信息
    cve_patch_file = open(save_path + "\\CVE Patch.txt", 'a', encoding="utf-8")
    print(cve_patch_file.name)
    for cve_patch_row in vulnerability_patch_row_list:
        # print(cve_patch_row)
        cve_patch_file.write(cve_patch_row)
        cve_patch_file.write('\n')
    cve_patch_file.close()

    for tag_div in patch_url_content_soup.find_all('div', attrs={'class', 'head'}):
        for tag_a in tag_div.find_all('a'):
            attrs_href = tag_a.get('href')
            code_url_list.append(attrs_href)

    # 获取修改之前文件代码
    previous_code_url_content = requests.get("https://git.kernel.org" + code_url_list[0]).content
    previous_code_url_content_soup = bs4.BeautifulSoup(previous_code_url_content, "html.parser")
    for tag_code in previous_code_url_content_soup.find_all('code'):
        previous_code = tag_code.get_text()
        vulnerability_previous_code_list.append(previous_code)

    # 存入修改前代码
    cve_previous_code_file = open(save_path + "\\CVE Previous Code.txt", 'a', encoding="utf-8")
    print(cve_previous_code_file.name)
    for cve_previous_code_row in vulnerability_previous_code_list:
        # print(cve_previous_code_row)
        cve_previous_code_file.write(cve_previous_code_row)
        cve_previous_code_file.write('\n')
    cve_previous_code_file.close()

    # 获取修改之后文件代码
    post_code_url_content = requests.get("https://git.kernel.org" + code_url_list[1]).content
    post_code_url_content_soup = bs4.BeautifulSoup(post_code_url_content, "html.parser")
    for tag_code in post_code_url_content_soup.find_all('code'):
        post_code = tag_code.get_text()
        vulnerability_post_code_list.append(post_code)

    # 存入修改后代码
    cve_post_code_file = open(save_path + "\\CVE Post Code.txt", 'a', encoding="utf-8")
    print(cve_post_code_file.name)
    for cve_post_code_row in vulnerability_post_code_list:
        cve_post_code_file.write(cve_post_code_row)
        cve_post_code_file.write('\n')
    cve_post_code_file.close()


# 捕获网页的一页中的漏洞的CVE编号
def get_vulnerability_id_list(internal_search_result_url):
    internal_vulnerability_id_list = []

    search_result_url_content = requests.get(internal_search_result_url).content
    search_result_url_content_soup = bs4.BeautifulSoup(search_result_url_content, "html.parser")
    for tag_div in search_result_url_content_soup.find_all('div', id='row'):
        for tag_table in tag_div.find_all('table'):
            for tag_tbody in tag_table.find_all('tbody'):
                for tag_strong in tag_tbody.find_all('strong'):
                    for tag_a in tag_strong.find_all('a'):
                        internal_vulnerability_id_list.append(tag_a.get_text())
    return internal_vulnerability_id_list


def main():
    # 输入查询关键字
    if debug:
        query_key_word = "linux+kernel"
    else:
        query_key_word = input('Key Word:').strip().replace(" ", "+")

    # 输入首末页码号
    if debug:
        beginning_pagination = 2
    else:
        while True:
            beginning_pagination = int(input("Beginning Pagination:"))
            if beginning_pagination >= 1:
                break

    if debug:
        closing_pagination = 4
    else:
        while True:
            closing_pagination = int(input("Closing Pagination:"))
            if closing_pagination >= beginning_pagination:
                break

    # 构造查询结果的网页链接
    for pagination in range(beginning_pagination, closing_pagination + 1):
        start_index_in_url = (pagination - 1) * 20
        search_result_url = "https://nvd.nist.gov/vuln/search/results" \
                            "?adv_search=false&form_type=basic" \
                            "&results_type=overview&search_type=all" \
                            "&query=" + query_key_word + "&startIndex=" + str(start_index_in_url)
        print(search_result_url)

        if lazy:
            get_vulnerability_code("https://nvd.nist.gov/vuln/detail/CVE-2017-16995", "CVE-2017-16995")

        # 捕获一页中的漏洞的CVE编号
        if not lazy:
            vulnerability_id_list = get_vulnerability_id_list(search_result_url)

            # 捕获每一个漏洞、补丁的代码
            for vulnerability_id_index in range(len(vulnerability_id_list)):
                vulnerability_id = vulnerability_id_list[vulnerability_id_index]
                vulnerability_detail_url = ("https://nvd.nist.gov/vuln/detail/" + vulnerability_id)
                print(vulnerability_detail_url)

                get_vulnerability_code(vulnerability_detail_url, vulnerability_id)


# 函数入口
if __name__ == "__main__":
    main()
