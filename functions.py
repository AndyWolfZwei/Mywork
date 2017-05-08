import re
from bs4 import BeautifulSoup
import urllib.request
import parserInfo
import chardet


class GetChineseInfo:
    def __init__(self):
        self.soup = BeautifulSoup("", 'html.parser')
        self.p = parserInfo.Parser()

    def _get_soup(self, urll):  # 返回soup对象
        req0 = urllib.request.Request(urll)
        req0.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
        req = urllib.request.urlopen(req0, timeout=8)
        char = chardet.detect(urllib.request.urlopen(req0).read())    # 自动识别编码
        soup = BeautifulSoup(req, "html.parser", from_encoding=char['encoding'])
        [script.extract() for script in soup.findAll('script')]
        [style.extract() for style in soup.findAll('style')]
        self.soup = soup
        return soup

    def get_crit_info(self, url2, tag='div', **kwargs):    # 要改标签    最好是div标签
        soup = GetChineseInfo._get_soup(self,url2)
        soups = soup.find(tag, **kwargs)   # *********************改这里*******************************
        reg1 = re.compile("<[^>]*>")
        try:
            content = reg1.sub('', soups.prettify())     # 如果获取页面所有中文 用soup.prettify   若获取body   用soups.p...
            return '~'.join(content.split())
        except Exception as e:
            print(e, url2)
            return None

    def get_c_info2(self):
        return '~'.join(self.soup.get_text().split())

if __name__ == "__main__":
    info = []
    url0 = 'http://cceb.dhu.edu.cn/article.do?method=showmax&id=60&pid=30&start=32&tx=0.8361615977042185'
    url = 'http://www.qwc.shu.edu.cn/Default.aspx?tabid=31537&ctl=Detail&mid=60165&Id=195583'
    temp = GetChineseInfo()
    re_infos = temp.get_crit_info(url, 'div', id="dnn_ContentPane")
    l = re_infos.split('~')  # 分割
    # print(re_infos)re_infos
    te = temp.p.parser_dir(l)
    print(te)

    # if len(list_info[n + count]) > 40:
    #     return re.sub(pattern, ' ', list_info[n + count].split()[0])
    # else:
    #     list_info[n + count] = re.sub(pattern, ' ', list_info[n + count])
    # return list_info[n + count]