import re


class Parser:
    def __init__(self):
        self.pattern = '的(研究|教学)(工作)?|研究方向|从事|[\(\)（）\[\]\-、.：:;；,，。是为长期主要【】]'

    def parser_dir(self, l):
        # if re.findall("研究方向|研究领域|主要从事", re_infos):  # *****现在页面中找关键字   判断下一个是否*****    研究方向|研究领域|主要从事|研究兴趣
        return self._search_dir(l)

    def method1(self, words):
        print('在本句找方向中')
        dirs = re.findall('研究(?:方向|领域|兴趣)[为是]?[：:]?(.*?)[。.、]|研究(?:方向|领域|兴趣)[为是]?[：:]?(.*?)$', words)
        if dirs:
            if dirs[0][0]:
                u = re.split("[、， ；,;.。:：]", dirs[0][0])  # 将第一句话分割 如果可以分割成多份 就判断字长度
                print('method1 话已分割')
                for i in range(0, len(u)):
                    print(u[i],u[i].isalnum())
                    if len(u[i]) > 4 and re.search(r'[\u4e00-\u9fa5]+',u[i]):
                        print('进行第%s次循环' % i)
                        return re.sub(self.pattern, ' ', u[i]).strip()
                else:
                    print('本句不能分割')
                    return re.sub(self.pattern, ' ', u[0]).strip()
            else:
                t = re.sub(self.pattern, ' ', dirs[0][1]).strip()
                return re.split(' ', t)[0]
        else:
            print("研究方向方法一失败")
            return ''

    def method2(self, list_info, n):
        count = 1
        print('在下一句找方向中')
        try:
            temp = ','.join(list_info[n + count].split())
            print(list_info[n + count])
            while len(list_info[n + count]) < 6 or not re.search(r'[\u4e00-\u9fa5]+',list_info[n + count]):
                print('在2进行第%s次循环' % count)
                list_info[n + count + 1] = re.sub(self.pattern, ' ', list_info[n + count + 1]).strip()
                temp = re.split(' ',list_info[n + count + 1])[0]
                count += 1
                print(temp)
            if re.search('研究方向|主要研究', list_info[n + count]) and len(temp) > 40:
                return Parser.method1(self, list_info[n + count])
            if len(re.split('[,、，]',list_info[n + count])) > 1:
                if len(re.split('[,、，]',list_info[n + count])[0]) < 3:
                    return re.split(' ', re.sub(self.pattern, ' ', list_info[n + count]).strip())[1]
                else:
                    print(re.split(' ', re.sub(self.pattern, ' ', list_info[n + count]).strip()))
                    return re.split(' ', re.sub(self.pattern, ' ', list_info[n + count]).strip())[0]
            return re.sub(self.pattern, '', temp)
        except Exception as e:
            print("研究方向方法二失败", e)
            return ''

    @staticmethod
    def parser_other_dir(soup):
        t = soup.select('#easytab_content_2')
        lis = []
        for i in t:
            lis.append(i.get_text())
        return re.sub('[\r\n]', '', ''.join(lis))

    def _search_dir(self, list_info):
        for n, words in enumerate(list_info):
            if re.findall("研究方向|研究领域|研究兴趣|研究专长|专业方向", words):  # *****在list中再找关键字 ******   (match search findall)
                print('找到研究方向')
                words = re.sub('[主要的]', '', words)
                if len(words) > 9 and not re.search('研究专长|及课题|从事专业',words):  # 如果研究方向所在长度小于6   执行在这句话里面找研究方向
                    return Parser.method1(self, words)
                else:               # 否则 在下一句找研究方向
                    return Parser.method2(self, list_info, n)
        else:
            return ' '

    @staticmethod
    def parser_qual(re_infos, l):
        u = re.findall("[\u4e00-\u9fa5]?[\u4e00-\u9fa5]?教授[^\u4e00-\u9fa5]|[\u4e00-\u9fa5]?[\u4e00-\u9fa5]?研究员"
                       "|[\u4e00-\u9fa5]?[\u4e00-\u9fa5]?工程师|讲师", re_infos)
        templates = ['名誉教授', '研究教授', '访问教授', '杰出教授', '校聘教授', '正高研究员', '高级工程师', '讲席教授', '助理教授', '兼职教授', '副高研究员', '资深研究员',
                     '中级研究员', '副研究员', '研究员', '助理研究员', '助理工程师', '工程师', '教授', '讲师']
        uu = re.sub('[~，]', '', str(u))
        for n0, words0 in enumerate(l):
            if re.search('职 ?称', words0):
                if l[n0 + 1] in templates:
                    print('method 1 success')
                    return l[n0 + 1]
            elif uu.count('副教授') > 1:
                return '副教授'
            else:
                for template in templates:
                    if uu.count(template) != 0:
                        return template
                else:
                    return "教授"

    @staticmethod
    def parser_email(re_infos):
        email = re.findall("[\w-]+(?:\.[\w!#$%&'*+/=?^_`{|}-]+)*@(?:[\w](?:[\w-]*[\w])?\.)"
                           "+[\w](?:[\w-]*[\w])?", re_infos)  # email
        if email:
            return email[0]
        else:
            return None
        # l = re_infos.split('~')
        # for n, t in enumerate(l):  # 针对读出@为[at] 情况
        #     if re.search("\[at\]", t):
        #         return l[n - 1] + '@' + l[n + 1]

    @staticmethod
    def parser_year(re_infos):
        years = re.findall(r'(19\d\d)[年.-]\d{0,2}[月.-]?\d{0,2}日?出?生', re_infos)
        if years:
            return years[0]
        else:
            years = re.findall('(?:出生|出生年月)[:：~]*?(19\d\d)[年.-]\d{0,2}[月.-]?\d{0,2}日?', re_infos)
            if years:
                return years[0]
            else:
                return ''


