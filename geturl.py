from bs4 import BeautifulSoup
import urllib.request
import re
import xlsxwriter
import functions
import parserInfo
from urllib.parse import urljoin
import time
import multiprocessing
import chardet
flag = 1
re_st = ''


class Spider:
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __init__(self, name, id0,tag, **kwargs):
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
            Spider._settle(self, names, urls, re_info, flag, ll)
        except Exception as e:
            print("_get_info  error!", e, 'The url is:', urls)
            self.info.clear()
            return

    def _settle(self, name, url, re_infos, flag0, l_t):
        l_split = re_infos.split('~')
        self.i += 1
        self.info.append(str(self.i))
        self.info.append(url)
        # print(self.f.soup.find('div',class_='font').h3.get_text())
        # self.info.append(self.f.soup.find('div',class_='font').h3.get_text())
        self.info.append(name)
        # ---------------------------EMAIL---------------------------------------------------------
        if self.parser_info.parser_email(re_infos):
            self.info.append(self.parser_info.parser_email(re_infos))
        else:
            self.info.clear()
            print('get no email! the url is:',url)
            return
        # ------------------------------------------------------------------------------------
        self.info.append("上海海事大学")
        self.info.append(self.name)
        self.info.append("上海")
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
        self.info.append(self.parser_info.parser_qual(re_infos, l_split))
        # ----------------------------导师资格----------------------------------------------------
        if re.findall("博士生导师|博导", re_infos):  # 匹配导师资格
            self.info.append("博士生导师")
        elif re.findall("硕士生导师|硕导", re_infos):
            self.info.append("硕士生导师")
        else:
            self.info.append('')
        # -----------------------------研究方向----适用于找下一句话------------------------------------
        if flag0 == 1:
            if re.search('1\d|\d1',self.parser_info.parser_dir(l_split)):
                self.info.append(self.parser_info.parser_dir(l_split))
            else:
                self.info.append(re.sub('1','',self.parser_info.parser_dir(l_split)))
        if flag0 == 2:       #
            self.info.append(self.parser_info.parser_other_dir(self.f.soup))
        if flag0 == 3:       # 找模板
            self.info.append(re.sub(r'研究方向|[\n：]','',self.f.soup.find('p',class_='arti_metas').get_text()))
        # ---------------------------------PHONE------------------------------------------------
        phone = re.findall("\D(0?2?1?[56]\d{3}-?\d{4}(?=\D)-?\d{0,3})", re_infos)  # phone
        if phone:
            self.info.append(phone[0])
        else:
            self.info.append("")
        # ------------------------------------------------------------------------------------
        self.info.append("310000")
        self.info.append("310100")
        self.info.append("")
        # ------------------------------------------------------------------------------------
        # print(self.info)
        # spider.write()
        print(self.info)
        l_t.append(self.info)
        if self.info:
            self.info = []

    @staticmethod
    def main(*urls):
        datas0 = []
        print(urls)
        for url in urls[0]:
            print(url)
            req = urllib.request.Request(url)
            req.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
            try:
                # req1 = urllib.request.urlopen(req)
                req1 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url)
            except Exception as e:
                print(e)
                req1 = urllib.request.urlopen(req, timeout=10)
            char = chardet.detect(urllib.request.urlopen(url).read())  # 自动识别编码
            if char['encoding'] == 'GB2312':
                char['encoding'] = 'gbk'
            soup = BeautifulSoup(req1, "html.parser", from_encoding=char['encoding'])
            texts = soup.select("a[href]")
            for text in texts:
                url0 = text['href']
                name = text.get_text(strip=True)
                name = name.replace('\xa0', '')
                # print(url0,name)
                global re_st
                if name.split():
                    if name and '查看详情' not in name:
                        if re.findall(re_st,url0):
                            temp = urljoin(url, url0.strip()) + "|" + name
                            datas0.append(temp)
                            print(temp.split("|"))
        # datas = list(set(datas0))   #  过滤重复
        # datas.sort()
        results = []
        for data in datas0:
            results.append(spider.pool.apply_async(spider.get_info, (data, l,)))
            # spider.get_info(data, l0,)
        spider.pool.close()
        spider.pool.join()
        for i in range(0,len(results)):
            if results[i].get() is not None:
                print(results[i].get())
        # except Exception as e:
        #     print('@@@',e)
        # for res in result:
        #     print(res.get())
        # print(self.info)
        # pool.close()
        # pool.join()


class Write(object):
    def __init__(self, name,lis):
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
        self.l = eval(lis)

    def writing(self):
        for i in range(0, len(self.l)):
            self.l[i][0] = i + 1
            for j in range(0, 17):
                self.worksheet.write(i+1, j, self.l[i][j])

    def end(self):
        self.workbook.close()

if __name__ == "__main__":
    start = time.time()
    re_st = '/xbh/teachers/team/'
    r_urls = [
        # 'http://cfl.shmtu.edu.cn/teacher2.aspx?id=',
        'http://www.xbharts.com/xbh/teachers/team/',
        # 'http://law.shmtu.edu.cn/index.aspx?lanmuid=95&sublanmuid=737',
        # 'http://law.shmtu.edu.cn/index.aspx?lanmuid=95&sublanmuid=738'
    ]
    # for i in range(132,139):
    #     r_urls.append('http://cfl.shmtu.edu.cn/teacher2.aspx?id=%s' %i)
    root_name = "徐悲鸿艺术学院"
    spider = Spider(root_name, 0, 'div', class_="nb-r-con")    # 0 获取部分内容 1 获取全部
    mgr = multiprocessing.Manager()
    l = mgr.list()
    spider.main(r_urls)
    write = Write(root_name, str(l))
    write.writing()
    write.end()
    print('ALL DONE!!!')
    end = time.time()
    print("@@@@@@@@@@@@@@@@@  %s" %(end - start))
