import requests, re
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from flask import current_app, abort



class jw_spider:
    def __init__(self):
        self.site=0
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
        self.total_grade_all = 0
        self.total_weight_all = 0
        self.age=16
        self.jws = requests.Session()
        self.base_url=''

    def set_age(self, age):
        self.age = age

    def login(self, login_data):
        self.base_url = current_app.config['JW_BASE_URL'][self.site]
        self.loginUrl = self.base_url + 'login.do'
        try:
            login_result = self.jws.post(self.loginUrl, data=login_data, headers=self.header)
            headers_res = dict(login_result.headers.items())
            if not headers_res.get('Pragma'):
                return '用户名或密码错误'
            return 'success'
        except:
            return '连接失败'

    def logout(self):
        self.base_url = current_app.config['JW_BASE_URL'][self.site]
        self.logoutUrl = self.base_url + 'exit.do?type=student'
        try:
            login_result = self.jws.post(self.logoutUrl)
            return
        except:
            abort(500)

    def get_grade(self, age=16, term=1):
        self.base_url = current_app.config['JW_BASE_URL'][self.site]
        term_tmp = term
        self.gradeUrl = self.base_url + 'student/studentinfo/achievementinfo.do?method=searchTermList'
        while term_tmp - 2 > 0:
            age += 1
            term_tmp -= 2
        term_str = '20' + str(age) + str(term_tmp)
        # post_grade_data = urllib.parse.urlencode({'termCode':term_str})
        # grade_request = urllib.request.Request( url = self.gradeUrl, data = post_grade_data.encode('utf-8') )
        # grade_result = self.opener.open(grade_request)
        post_grade_data = {'termCode': term_str}
        grade_result = self.jws.post(self.gradeUrl, data=post_grade_data, headers=self.header)
        mygradepage = grade_result.content.decode('utf-8')
        soup = BeautifulSoup(mygradepage, 'lxml')
        trs = soup.find_all('tr', class_=['TABLE_TR_02', 'TABLE_TR_01'])
        lesson_names = []
        lesson_type = []
        lesson_weights = []
        lesson_grades = []
        for j1 in range(len(trs)):
            _soup = BeautifulSoup(str(trs[j1]), 'lxml')
            tds = _soup.find_all('td')
            # tds[2] = alignment(str(tds[2]),20)
            for j2 in range(len(tds)):
                tds[j2] = tds[j2].get_text().strip()
            # for td in tds:
            # td = td.get_text().strip()
            lesson_names.append(str(tds[2]))
            lesson_type.append(tds[4])
            tds[5] = re.sub("[^\d.]", "", tds[5])
            try:
                tds[5] = int(float(tds[5]))
            except:
                tds[5] = 0
            lesson_weights.append(tds[5])
            # lesson_grades.append(str(int(tds[6])))
            tds[6] = re.sub("[^\d.]", "", tds[6])
            try:
                tds[6] = int(float(tds[6]))
            except:
                tds[6] = 0
            lesson_grades.append(tds[6])
        return [lesson_names, lesson_type, lesson_weights, lesson_grades]
        # for j in range(len(trs)):
        #     print('%s %2s  %1d  %3d' % (lesson_names[j], lesson_type[j], lesson_weights[j], lesson_grades[j]))

        # total_grade = 0
        # total_weight = 0

        # for j in range(len(trs)):
        #     total_grade += lesson_weights[j] * lesson_grades[j]
        #     total_weight += lesson_weights[j]
        # self.total_grade_all += total_grade
        # self.total_weight_all += total_weight
        # gpa = total_grade / total_weight / 20
        # print('第%d学期全部课程学分绩为：%f\n' % (term, gpa))
    ###need to be deleted
    def alignment(self, str1, space, align='left'):
        length = len(str1.encode('gb2312'))
        space = space - length if space >= length else 0
        if align == 'left':
            str1 = str1 + ' ' * space
        elif align == 'right':
            str1 = ' ' * space + str1
        elif align == 'center':
            str1 = ' ' * (space // 2) + str1 + ' ' * (space - space // 2)
        return str1