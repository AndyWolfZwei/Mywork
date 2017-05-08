from bs4 import BeautifulSoup
import urllib.request
import re
import xlsxwriter
import functions
import parserInfo
from urllib.parse import urljoin

flag = 1


class Spider:
    def __init__(self, name, tag, **kwargs):
        self.name = name
        self.workbook = xlsxwriter.Workbook(r'C:\Users\happytreefriend\Desktop\working\excel\DHU'+name+'.xlsx')
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
        self.info = []
        self.i = 1
        self.f = functions.GetChineseInfo()
        self.parser_info = parserInfo.Parser()
        self.tag = tag
        self.kwargs = kwargs

    def _get_info(self, strs):
        names = strs.split("|")[1]
        urls = strs.split("|")[0]
        global flag
        try:
            re_info = self.f.get_crit_info(urls,self.tag,**self.kwargs)

            spider._settle(names, urls, re_info, flag)
        except Exception as e:
            print("_get_info  error!", e, 'The url is:', urls)
            self.info.clear()
            return

    def _settle(self, name, url, re_infos, flag0):
        l = re_infos.split('~')
        self.info.append(str(self.i))
        self.info.append(url)
        self.info.append(name)
        # ---------------------------EMAIL---------------------------------------------------------
        if self.parser_info.parser_email(re_infos):
            self.info.append(self.parser_info.parser_email(re_infos))
        else:
            self.info.clear()
            print('get no email! the url is:',url)
            return
        # ------------------------------------------------------------------------------------
        self.info.append("东华大学")
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
        self.info.append(self.parser_info.parser_qual(re_infos, l))
        # ----------------------------导师资格----------------------------------------------------
        if re.findall("博士生导师|博导", re_infos):  # 匹配导师资格
            self.info.append("博士生导师")
        elif re.findall("硕士生导师|硕导", re_infos):
            self.info.append("硕士生导师")
        else:
            self.info.append('')
        # -----------------------------研究方向----适用于找下一句话------------------------------------
        if flag0 == 1:
            self.info.append(self.parser_info.parser_dir(l))
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
        print(self.info)
        spider.write()
        if self.info:
            self.info = []

    def write(self):
        self.worksheet.write(self.i, 0,  self.info[0])
        self.worksheet.write(self.i, 1,  self.info[1])
        self.worksheet.write(self.i, 2,  self.info[2])
        self.worksheet.write(self.i, 3,  self.info[3])
        self.worksheet.write(self.i, 4,  self.info[4])
        self.worksheet.write(self.i, 5,  self.info[5])
        self.worksheet.write(self.i, 6,  self.info[6])
        self.worksheet.write(self.i, 7,  self.info[7])
        self.worksheet.write(self.i, 8,  self.info[8])
        self.worksheet.write(self.i, 9,  self.info[9])
        self.worksheet.write(self.i, 10, self.info[10])
        self.worksheet.write(self.i, 11, self.info[11])
        self.worksheet.write(self.i, 12, self.info[12])
        self.worksheet.write(self.i, 13, self.info[13])
        self.worksheet.write(self.i, 14, self.info[14])
        self.worksheet.write(self.i, 15, self.info[15])
        self.worksheet.write(self.i, 16, self.info[16])
        self.i += 1

    def end(self):
        self.workbook.close()

    @staticmethod
    def main():
        datas = []
        urls = [
            'http://pe.dhu.edu.cn/3370/list1.htm',
            'http://pe.dhu.edu.cn/3370/list2.htm','http://pe.dhu.edu.cn/3370/list3.htm']
        # url = 'http://ices.shufe.edu.cn/Detail.aspx?ID=1364&TypeID=101&WebID=17'
        # for i in range(4,9):
        #     url = 'http://cise.ecust.edu.cn/2011/0615/c7766a5514%s/page.htm' %i
        # url = 'http://web.dhu.edu.cn/cist/2969/list.htm'
        for url in urls:
            req = urllib.request.Request(url)
            req.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
            texts = urllib.request.urlopen(req,timeout=8).read()
            soup = BeautifulSoup(texts, "html.parser")
            texts = soup.select("a[href]")
            for text in texts:
                url0 = text['href']
                name = text.get_text()
                name = name.strip()
                if name.split():
                    if name:
                        if 'page.htm' in url0:
                            temp = urljoin(url, url0) + "|" + name
                            datas.append(temp)
                            print(temp.split("|"))
        # datas = list(set(datas))   # 过滤重复
        # datas.sort()
        for data in datas:
            if data:
                spider._get_info(data)
            else:
                return

    def main2(self):    # ****************************信息在一个url情况   此时改if_name__ 中的main函数
        urls = ['http://cise.ecust.edu.cn/2011/0615/c7766a55144/page.htm',
                'http://cise.ecust.edu.cn/2011/0615/c7766a55149/page.htm',
                'http://cise.ecust.edu.cn/2011/0615/c7766a55148/page.htm',
                'http://cise.ecust.edu.cn/2011/0615/c7766a55147/page.htm',
                'http://cise.ecust.edu.cn/2011/0615/c7766a55146/page.htm',
                'http://cise.ecust.edu.cn/2011/0615/c7766a55145/page.htm']
        for url in urls:
            re_infos = self.f.get_crit_info(url, self.tag, **self.kwargs).split('办公地址')
            for re_info in re_infos:
                t_list = [x for x in re_info.split('~') if x]
                try:
                    if re.search('@', t_list[-1]):
                        print(t_list)
                        Spider._settle2(self, url, t_list)
                except:
                    self.info.clear()
                    continue

    def _settle2(self,url,t_list):
        self.info.append(str(self.i))
        self.info.append(url)
        gender = ''
        prof = ''
        dir0 = ''
        phone = ''
        for n,mess in enumerate(t_list):
            if re.search('[男女]',mess):
                gender = re.search('[男女]',mess).group()
                prof = t_list[n].split('，')[1]
                if len(t_list[n-1]) == 1:
                    self.info.append(t_list[n - 2] + t_list[n - 1])
                else:
                    self.info.append(t_list[n-1])
            if re.search('研究兴趣|研究领域|主讲课程',mess):
                dir0 = t_list[n + 1]
            if re.search('联系电话', mess):
                phone = t_list[n + 1]
        self.info.append(t_list[-1])
        self.info.append("华东理工大学")
        self.info.append(self.name)
        self.info.append("上海")
        self.info.append('')
        self.info.append(gender)
        self.info.append('博士')
        self.info.append(prof)
        self.info.append('')
        self.info.append(dir0)
        self.info.append(phone)
        self.info.append("310000")
        self.info.append("310100")
        self.info.append("")
        print(self.info)
        spider.write()
        if self.info:
            self.info = []

if __name__ == "__main__":
    spider = Spider("体育部11", 'div', id="container_content")
    spider.main()
    spider.end()

