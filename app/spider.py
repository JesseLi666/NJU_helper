import requests
import re
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from flask import current_app, abort


class jw_spider:
    def __init__(self):
        self.site = 0
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
        self.total_grade_all = 0
        self.total_weight_all = 0
        self.age = 16
        self.jws = requests.Session()
        self.base_url = ''

    def set_age(self, age):
        self.age = age

    def login(self, login_data):
        self.base_url = current_app.config['JW_BASE_URL'][self.site]
        self.loginUrl = self.base_url + 'login.do'
        try:
            login_result = self.jws.post(self.loginUrl, data=login_data, headers=self.header)
            headers_res = dict(login_result.headers.items())
            if not headers_res.get('pragma') and not headers_res.get('Pragma'):
                return '用户名或密码错误'
            return 'success'
        except:
            return '连接失败，请尝试更换站点'

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
        # lesson_names = []
        # lesson_type = []
        # lesson_weights = []
        # lesson_grades = []
        temp_all = []
        for j1 in range(len(trs)):
            temp = []
            _soup = BeautifulSoup(str(trs[j1]), 'lxml')
            tds = _soup.find_all('td')
            # tds[2] = alignment(str(tds[2]),20)
            for j2 in range(len(tds)):
                tds[j2] = tds[j2].get_text().strip()
            # for td in tds:
            # td = td.get_text().strip()
            # lesson_names.append(str(tds[2]))
            temp.append(str(tds[2]))
            # lesson_type.append(tds[4])
            temp.append(str(tds[4]))
            tds[5] = re.sub("[^\d.]", "", tds[5])
            try:
                tds[5] = int(float(tds[5]))
            except:
                tds[5] = 0
            # lesson_weights.append(tds[5])
            temp.append(str(tds[5]))
            # lesson_grades.append(str(int(tds[6])))
            tds[6] = re.sub("[^\d.]", "", tds[6])
            try:
                tds[6] = int(float(tds[6]))
            except:
                tds[6] = 0
            temp.append(str(tds[6]))
            temp_all.append(temp)
            # lesson_grades.append(tds[6])
        return temp_all
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
    # need to be deleted
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

    def get_course(self):
        self.base_url = current_app.config['JW_BASE_URL'][self.site]
        # self.base_url = 'http://jw.nju.edu.cn:8080/jiaowu/'
        self.courseUrl = self.base_url + 'student/teachinginfo/courseList.do?method=currentTermCourse'
        # course_result = self.jws.get(url=self.courseUrl)
        course_result = self.jws.get(url=self.courseUrl)
        mycoursepage = course_result.content.decode('utf-8')
        soup = BeautifulSoup(mycoursepage, 'lxml')
        trs = soup.find_all('tr', class_=['TABLE_TR_02', 'TABLE_TR_01'])
        courses = []
        for j1 in range(len(trs)):
            temp = []
            _soup = BeautifulSoup(str(trs[j1]), 'lxml')
            tds = _soup.find_all('td')
            # print(tds[5].get_text())

            for j2 in range(len(tds)):
                # tds[j2] = tds[j2].get_text().strip(' \t')
                if j2 == 5:
                    tds[j2] = BeautifulSoup(tds[j2].encode(
                        'utf-8').decode('utf-8').replace('<br/>', '\n'), 'lxml')
                tds[j2] = tds[j2].get_text().strip()

            temp.append(str(tds[2]))
            temp.append(str(tds[4]))
            temp.append(str(tds[5]))
            temp.append(str(tds[0]))  # 编号
            temp.append(str(tds[7]))  # 类型
            temp.append(str(tds[3]))  # 校区
            courses.append(temp)
            # print(tds[5])
        return courses

    def deal_course(self, c):
        # print(c1)
        # c2 = re.sub(r'周(开始)', r'\1', c)
        c3 = c.split('\n')
        end = 19
        res = []
        res_except = []
        dict = {u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'日': 7}
        for c4 in c3:
            # print(c4)
            try:
                week = []
                r1 = re.findall(r'第\d+周 ', c4)
                for rr1 in r1:
                    week.append(int(re.sub(r'第(\d+)周 ', r'\1', rr1)))
                r2 = re.findall(r'\d+-\d+周', c4)
                for rr2 in r2:
                    for i in range(int(re.sub(r'(\d+)-(\d+)周', r'\1', rr2)), int(re.sub(r'(\d+)-(\d+)周', r'\2', rr2)) + 1):
                        week.append(i)
                r3 = re.findall(r'从第\d+周开始:.周 ', c4)
                for rr3 in r3:
                    danshaung = re.sub(r'从第\d+周开始:(.)周 ', r'\1', rr3)
                    if danshaung == '单':
                        mod = 1
                    elif danshaung == '双':
                        mod = 0
                    else:
                        mod = -1
                    for i in range(int(re.sub(r'从第(\d+)周开始:.周 ', r'\1', rr3)), end):
                        if i % 2 == mod:
                            week.append(i)
                r4 = re.findall(r' .周', c4)
                # print(r4)
                for rr4 in r4:
                    danshaung = re.sub(r' (.)周', r'\1', rr4)
                    # print(danshaung)
                    if danshaung == '单':
                        mod = 1
                    elif danshaung == '双':
                        mod = 0
                    else:
                        mod = -1
                    for i in range(1, end):
                        if i % 2 == mod:
                            week.append(i)
                day = dict[c4[1]]
                jieshu = [int(re.sub(r'[^\d]+第(\d+)-(\d+)节.+', r'\1', c4)),
                          int(re.sub(r'[^\d]+第(\d+)-(\d+)节.+', r'\2', c4))]
                c5 = c4.split('周')
                jiaoshi = c5[len(c5) - 1].strip()
                res.append([week, day, jieshu, jiaoshi])
            except:
                res_except.append(c4)

        return [res, res_except]

    def create_courses(self, course_result, week=1):
        courses = []
        courses_except = []
        index = 0
        for i in range(0, 7):
            t1 = []
            for j in range(0, 11):
                t2 = ['', []]
                t1.append(t2)
            courses.append(t1)
        for t in course_result:
            course = self.deal_course(t[2])
            if course[1] != []:
                for te in course[1]:
                    courses_except.append([t[0], t[1], te, index])
            # print(course)
            for c in course[0]:
                if week in c[0]:
                    # print(courses)
                    for i in range(c[2][0], c[2][1] + 1):
                        # print(courses[c[1]-1][i-1][1])
                        courses[c[1] - 1][i - 1][1].append(index)

                    #     courses[c[1]-1][i-1][2] = 'normal'
                    # courses[c[1]-1][c[2][0]-1][2] = 'start'
                    if len(courses[c[1] - 1][c[2][0] - 1][1]) == 1:
                        courses[c[1] - 1][c[2][0] - 1][0] = t[0]
                    if (c[2][1] > c[2][0]) and len(courses[c[1] - 1][c[2][0]][1]) == 1:
                        courses[c[1] - 1][c[2][0]][0] = c[3]
                    if (c[2][1] > c[2][0] + 1) and len(courses[c[1] - 1][c[2][0] + 1][1]) == 1:
                        courses[c[1] - 1][c[2][0] + 1][0] = t[1]
            index += 1
        return [courses, courses_except]
