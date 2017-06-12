import sys
from bs4 import BeautifulSoup
import re
import xlsxwriter
from selenium import webdriver
import functions
import parserInfo
from urllib.parse import urljoin
import time
import multiprocessing
import chardet
import requests
from xpinyin import Pinyin, get_init_name
email_tail = '@lsu.edu.cn'
flag = 1
re_st = ''
sel = 0


class Spider:
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __init__(self, name, id0, tag, **kwargs):
        self.name = name
        self.info = []
        self.f = functions.GetChineseInfo()
        self.parser_info = parserInfo.Parser()
        self.tag = tag
        self.kwargs = kwargs
        self.pool = multiprocessing.Pool(8)
        self.i = 1
        self.id = id0

    def get_info(self, strs, l_in):
        names = strs.split("|")[1]
        urls = strs.split("|")[0]
        ll = l_in
        # print(names,urls)
        global flag
        try:
            re_info = self.f.get_crit_info(urls, self.id, self.tag, **self.kwargs)
            Spider.settle(self, names, urls, re_info, flag, ll)
        except Exception as e:
            s = sys.exc_info()
            print("Error '%s' happened on line %d,the error is %s" % (s[1], s[2].tb_lineno, e), 'the url is:', urls)
            # print("_get_info  error!", e, 'The url is:', urls)
            self.info.clear()
            return

    def settle(self, name, url, re_infos, flag0, l_t):
        noemail = ''
        l_split = re_infos.split('~')
        self.i += 1
        self.info.append(str(self.i))
        self.info.append(url)
        # name = self.f.soup.find('div',class_='shownews').get_text().split(' ')[0]
        # name = name.replace('\n','')
        self.info.append(name)
        # ---------------------------EMAIL---------------------------------------------------------
        e = self.parser_info.parser_email(re_infos)
        e = re.sub('qq.cn', 'qq.com', str(e))
        if e and 'None' not in e and 'hys3054103@126.com' not in e:
            self.info.append(e)
        else:
            global email_tail
            print('get no email! the url is:', url)
            noemail = '1'
            p = Pinyin()
            q = get_init_name()
            self.info.append(q.main(name[1:]) + p.get_pinyin(name[0])+email_tail)
        # email = self.f.soup.find('a',href=re.compile('^mailto'))['href']
        # if email:
        #     self.info.append(email)
        # ------------------------------------------------------------------------------------
        self.info.append("丽水学院")
        self.info.append(self.name)
        self.info.append("丽水")
        # -----------------------------YEAR-------------------------------------------------------
        self.info.append(self.parser_info.parser_year(re_infos))
        # ------------------------------GENDER---------------------------------------------------
        gender = re.findall("[，。,.、~]([男女])[,，。.、~]", re_infos)  # 性别
        if len(gender) == 0:
            self.info.append('')
        else:
            self.info.append(gender[0])
        # ------------------------------博士硕士学士------------------------------------------------------
        if re.search("博士", re_infos):  # 匹配学历
            self.info.append("博士")
        elif re.search("硕士", re_infos):
            self.info.append("硕士")
        elif re.search("学士", re_infos):
            self.info.append("学士")
        else:
            self.info.append('博士')
        # ----------------------------职称---------------------------------------------------
        self.info.append(self.parser_info.parser_qual(re_infos, l_split, name))
        # ----------------------------导师资格----------------------------------------------------
        if re.findall("博士生导师|博导", re_infos):  # 匹配导师资格
            self.info.append("博士生导师")
        elif re.findall("硕士生导师|硕导", re_infos):
            self.info.append("硕士生导师")
        else:
            self.info.append('')

        # -----------------------------研究方向----适用于找下一句话------------------------------------
        if flag0 == 1:
            if re.search('1\d|\d1', self.parser_info.parser_dir(l_split)):
                self.info.append(self.parser_info.parser_dir(l_split))
            else:
                self.info.append(re.sub('1', '', self.parser_info.parser_dir(l_split)))
        if flag0 == 2:       # 同3
            self.info.append(self.parser_info.parser_other_dir(self.f.soup))
        if flag0 == 3:       # 找模板
            self.info.append(re.sub(r'研究方向|[\n：]', '', self.f.soup.find('div', class_='infoview2').get_text()).strip())
        # ---------------------------------PHONE------------------------------------------------
        phone = re.findall("\D(0?2?1?[568]\d{3}-?\d{4}(?=\D)-?\d{0,3})", re_infos)  # phone
        if phone:
            self.info.append(phone[0])
        else:
            self.info.append("")

        # ------------------------------------------------------------------------------------
        print(noemail, '@@@@@@@@@@')
        self.info.append("330000")
        self.info.append("331100")
        self.info.append("")
        if noemail == '1':
            self.info.append('*')
        else:
            self.info.append('')
        # ------------------------------------------------------------------------------------
        # print(self.info)
        # spider.write()
        print(self.info)
        l_t.append(self.info)
        if self.info:
            self.info = []


def main(*urls):
    datas0 = []
    print(urls)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', }
    for url in urls[0]:
        print(url)
        if sel == 0:
            try:
                req1 = requests.get(url, headers=headers, timeout=10).content
            except Exception as e:
                print(e)
                req1 = requests.get(url, headers=headers, timeout=10).content
        if sel == 1:
            driver = webdriver.PhantomJS()
            driver.get(url)
            req1 = driver.page_source.encode()
        char = chardet.detect(req1)  # 自动识别编码
        if char['encoding'] == 'GB2312':
            char['encoding'] = 'gbk'
        soup = BeautifulSoup(req1, "html.parser", from_encoding=char['encoding'])
        texts = soup.select("a[href]")
        for text in texts:
            url0 = text['href']
            name = text.get_text()
            name = name.replace('\xa0', '')
            name = re.sub('(个人)?简介|(高级)?工程师|教授|副教授|院士|研究员|讲师|实验师|[()（）【】]|简历|客座|名誉|博士',
                          '', ''.join([zi.strip() for zi in name]))
            name = re.split('-|－|\d|：', name)[0]
            global re_st
            if name.strip():
                if name and '预览' not in name:
                    if re.search(re_st, url0):
                        try:
                            temp = urljoin(url, url0.strip()) + "|" + name
                            datas0.append(temp)
                            print(temp.split("|"))
                        except KeyError:
                            print('main.get name url error')
                            continue
    # datas = list(set(datas0))   #  过滤重复
    # datas.sort()
    results = []
    for data in datas0:
        results.append(spider.pool.apply_async(spider.get_info, (data, l,)))
        # spider.get_info(data, l0,)
    spider.pool.close()
    spider.pool.join()
    for ii in range(0, len(results)):
        if results[ii].get() is not None:
            print(results[ii].get())


class Write(object):
    def __init__(self, name, lis):
        self.workbook = xlsxwriter.Workbook(r'C:\Users\happytreefriend\Desktop\working\excel\\'+name+'.xlsx')
        self.worksheet = self.workbook.add_worksheet(name)
        self.worksheet.set_column('B:B', 40)
        self.worksheet.set_column('D:D', 30)
        self.worksheet.set_column('L:L', 12)
        self.worksheet.set_column('M:M', 20)
        self.worksheet.write('A1', 'Id')
        self.worksheet.write('B1', 'Url')
        self.worksheet.write('C1', 'Name')
        self.worksheet.write('D1', 'Email')
        self.worksheet.write('E1', 'Unit')
        self.worksheet.write('F1', '院系')
        self.worksheet.write('G1', 'Address')
        self.worksheet.write('H1', '年份')
        self.worksheet.write('I1', '性别')
        self.worksheet.write('J1', '学位')
        self.worksheet.write('K1', '职称')
        self.worksheet.write('L1', '导师资格')
        self.worksheet.write('M1', '研究方向')
        self.worksheet.write('N1', '电话')
        self.worksheet.write('O1', '省代码')
        self.worksheet.write('P1', '市代码')
        self.worksheet.write('Q1', '研究领域代码')
        self.worksheet.write('R1', 'ifemail')
        self.l = eval(lis)

    def writing(self):
        for ii in range(0, len(self.l)):
            self.l[ii][0] = ii + 1
            for j in range(0, 18):
                self.worksheet.write(ii+1, j, self.l[ii][j])

    def end(self):
        self.workbook.close()


if __name__ == "__main__":
    start = time.time()
    re_st = 'jgfc/detail.asp'
    r_urls = [
        'http://lxy.zust.edu.cn/SPage.asp?BigCategoryID=1&SmallCategoryID=8&CategoryType=2',
        # 'http://www.zjhys.cn/rcpy/dsdw/list65_2.html',
        # 'http://jgxy.zjou.edu.cn/szdw/bsfc.htm',
        # 'http://shxy.zjou.edu.cn/list1.jsp?a8t=2&a8p=2&a8c=10&urltype=tree.TreeTempUrl&wbtreeid=1033',
        # 'http://ghxy.zjou.edu.cn/erji.jsp?a6t=5&a6p=5&a6c=13&urltype=tree.TreeTempUrl&wbtreeid=2495',
    ]
    r_urls1 = ['http://yjg.hznu.edu.cn/rcpy/dsmc/index.shtml']
    for i in range(1, 5):
        # for j in range(1,6):
            r_urls1.append('http://www.ojc.zj.cn/Col/Col64/Index_%s.aspx' % (i,))
    root_name = "理学院"
    spider = Spider(root_name, 1, 'div', id=re.compile("article_disp"))  # 0 获取部分内容 1 获取全部
    mgr = multiprocessing.Manager()
    l = mgr.list()
    main(r_urls)   # @@@@@@@@@@@@@@改这里@@@@@@@@@@@@
    write = Write(root_name, str(l))
    write.writing()
    write.end()
    print('ALL DONE!!!')
    end = time.time()
    print("@@@@@@@@@@@@@@@@@  %s" % (end - start))
