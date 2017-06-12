import re
from bs4 import BeautifulSoup
import chardet
import parserInfo
import requests

class GetChineseInfo:
    def __init__(self):
        self.soup = BeautifulSoup("", 'html.parser')
        self.p = parserInfo.Parser()

    def _get_soup(self, urll):  # 返回soup对象
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', }
        try:
            req = requests.get(urll, headers=headers, timeout=10)
        except Exception as e:
            print(e)
            req = requests.get(urll, headers=headers, timeout=10)
        char = chardet.detect(req.content)    # 自动识别编码
        if char['encoding'] == 'GB2312':
            char['encoding'] = 'gbk'
        soup = BeautifulSoup(req.content, "html.parser", from_encoding=char['encoding'])
        [script.extract() for script in soup.findAll('script')]
        [style.extract() for style in soup.findAll('style')]
        self.soup = soup
        return soup

    def get_crit_info(self, url2, num=0,tag='div', **kwargs):    # 要改标签    最好是div标签
        soup = GetChineseInfo._get_soup(self,url2)
        soups = soup.find(tag, **kwargs)   # *********************改这里*******************************
        reg1 = re.compile("<[^>]*>")
        try:
            if num == 0:
                content0 = reg1.sub('', soups.prettify())     # 如果获取页面所有中文 用soup.prettify   若获取body   用soups.p...
                return '~'.join(content0.split())
            if num == 1:
                content = reg1.sub('', soup.prettify())
                return '~'.join(content.split())
        except Exception as e:
            print(e, url2)
            return None

    def get_c_info2(self):
        return '~'.join(self.soup.get_text().split())

if __name__ == "__main__":
    info = []
    parser_info = parserInfo.Parser()
    url0 = 'http://cceb.dhu.edu.cn/article.do?method=showmax&id=60&pid=30&start=32&tx=0.8361615977042185'
    url = 'http://sc.zjou.edu.cn/info/1257/2707.htm'
    temp = GetChineseInfo()
    re_infos = temp.get_crit_info(url, 0, 'div', id="vsb_content")
    l = re_infos.split('~')  # 分割
    print(l)
    te = temp.p.parser_dir(l)
    print(te)


    # if len(list_info[n + count]) > 40:
    #     return re.sub(pattern, ' ', list_info[n + count].split()[0])
    # else:
    #     list_info[n + count] = re.sub(pattern, ' ', list_info[n + count])
    # return list_info[n + count]