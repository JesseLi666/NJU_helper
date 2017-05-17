# coding: utf-8
import json
import re
import requests
import datetime
from flask import render_template, redirect, url_for, request, flash,\
    current_app
from flask_login import current_user, login_user, logout_user, login_required

from ..spider import jw_spider
from . import helper
from .forms import JWLoginForm, wechat_JWLoginForm, suggestForm
from .. import db
from ..decorators import jw_login_required
from ..models import User, AESCipher
from .mail import send_email_by_suggestion


@helper.route('/jw_login', methods=['GET', 'POST'])
def jw_login():
    form = JWLoginForm()

    if form.validate_on_submit():
        site_choose = form.site.data
        data = {
            'userName': form.number.data,
            'password': form.password.data
        }

        user = User.query.filter_by(user_number=form.number.data).first()
        if user is None:
            new_user = User()
            new_user.user_number = form.number.data
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(user_number=form.number.data).first()

        user.spd = jw_spider()
        user.spd.site = int(site_choose)
        user.spd.age = int(form.number.data[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res == 'success':
            login_user(user)
            return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
        else:
            flash(login_res)
    return render_template('helper/login.html', form=form)


@helper.route('/grade')
@jw_login_required
def get_grade_start():
    return redirect(url_for('helper.get_grade', term=1))


@helper.route('/grades/<int:term>', methods=['GET', 'POST'])
# @login_required
@jw_login_required
def get_grade(term):
    try:
        grade_res = current_user.spd.get_grade(age=current_user.spd.age, term=term)
    except:
        grade_res = [['null', 'null', 0, 0]]
    # cnt = len(grade_res)
    cur_year = datetime.datetime.now().year % 2000
    total_term = (cur_year - current_user.spd.age) * 2 - 1
    return render_template('helper/grade.html', grades=grade_res, terms=total_term, term_now=term, base_url=current_user.spd.base_url)


@helper.route('/jw_logout')
# @login_required
@jw_login_required
def jw_logout():
    current_user.spd.logout()
    logout_user()
    return redirect(url_for('helper.jw_login'))


@helper.route('/_cal', methods=['GET', 'POST'])
def calculate():
    # print('?')
    res = request.form.getlist('g')
    total_weight = 0
    total_grade = 0
    for r in res:
        weight = int(re.sub(r',\d+', '', r))
        grade = int(re.sub(r'\d+,', '', r))
        total_grade += weight * grade
        total_weight += weight
    # print(res[0])
    if(total_weight != 0):
        gpa = total_grade / total_weight / 20
        gpa = str('%.3f' % gpa)
        # print(gpa)
    else:
        gpa = 'wrong!'
    return gpa


@helper.route('/_cal2', methods=['GET', 'POST'])
def calculate_std():
    # print('?')
    res = request.form.getlist('g')
    total_weight = 0
    total_grade = 0
    for r in res:
        weight = int(re.sub(r',\d+', '', r))
        grade = int(re.sub(r'\d+,', '', r))
        if grade >= 90:
            total_grade += weight * 4
        elif grade >= 80:
            total_grade += weight * 3
        elif grade >= 70:
            total_grade += weight * 2
        elif grade >= 60:
            total_grade += weight

        total_weight += weight
    # print(res[0])
    if(total_weight != 0):
        gpa = total_grade / total_weight
        gpa = str('%.3f' % gpa)
        # print(gpa)
    else:
        gpa = 'wrong!'
    return gpa

@helper.route('/_cal3', methods=['GET', 'POST'])
def calculate_wes():
    # print('?')
    res = request.form.getlist('g')
    total_weight=0
    total_grade=0
    for r in res:
        weight = int(re.sub(r',\d+', '', r))
        grade = int(re.sub(r'\d+,', '', r))
        if grade >= 85:
            total_grade += weight * 4
        elif grade >= 75:
            total_grade += weight * 3
        elif grade >= 60:
            total_grade += weight * 2
        else:
            total_grade += weight * 1

        total_weight += weight
    # print(res[0])
    if(total_weight != 0):
        gpa = total_grade/total_weight
        gpa = str('%.3f' % gpa)
        # print(gpa)
    else:
        gpa = 'wrong!'
    return gpa


@helper.route('/cal')
@jw_login_required
def grade_cal():
    total_term = (16 - current_user.spd.age) * 2 + 1
    grades = []
    for i in range(1, total_term + 1):
        temp_grade = current_user.spd.get_grade(age=current_user.spd.age, term=i)
        grades.append(temp_grade)
        # for ls in temp_grade:
        #     grades.append(ls)

    return render_template('helper/cal.html', grades=grades)


@helper.route('/wechat/grade')
def get_wechat_grade_start():
    # global openid
    openid = request.args.get('openid')
    if not openid:
        return redirect(url_for('helper.get_grade',term=1))
    else:
        user = User.query.filter_by(wechat_id=openid).first()
        # current_app.logger.info(user.password)
        if user is None or user.wechat_id is None:
            return redirect(url_for('helper.jw_wechat_login', openid=openid))
        try:
            current_app.logger.info('%s %s grade'%(openid, user.user_number))
            pwd = user.password
            cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
            pwd = cipher.decrypt(pwd)
        except:
            return redirect(url_for('helper.jw_wechat_login', openid=openid))

        data = {
            'userName': user.user_number,
            'password': pwd
        }
        current_app.logger.info('username=%s' % data.get('userName'))
        current_app.logger.info('password=%s' % data.get('password'))
        user.spd = jw_spider()
        user.spd.site = 0
        user.spd.age = int(user.user_number[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res == 'success':
            login_user(user)
            # return redirect(url_for('helper.get_grade_start', num=user.user_number))
            # if request.args.get('next'):
            #     next = url_for('main.index')+request.args.get('next')
            #     print(next)

            return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
        else:
            user.spd.site = 1
            login_res = user.spd.login(login_data=data)
            if login_res == 'success':
                login_user(user)
                return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
            else:
                return redirect(url_for('helper.jw_wechat_login', type=1, openid=openid))


@helper.route('/wechat/jw_login', methods=['GET', 'POST'])
def jw_wechat_login(type=0):
    form = wechat_JWLoginForm()
    if type == 1:
        flash('您绑定的账号密码有误，请重新绑定！')
    if form.validate_on_submit():
        openid = request.args.get('openid')
        user = User.query.filter_by(wechat_id=openid).first()
        site_choose = form.site.data
        data = {
            'userName': form.number.data,
            'password': form.password.data
        }
        if user is None:
            new_user = User()
            new_user.wechat_id = openid
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(wechat_id=openid).first()

        # user.create_spd()
        if form.rem_wechat.data == True:
            # 加密账号密码并储存
            user.remember_me = True
            user.user_number = form.number.data
            current_app.logger.info('%s %s new_login' % (openid, user.user_number))
            cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
            print("form.password.data", form.password.data)
            pwd = cipher.encrypt(form.password.data)
            user.password = pwd
            db.session.add(user)
            db.session.commit()
        user.spd = jw_spider()
        user.spd.site = int(site_choose)
        # user.spd.set_age(int(form.number.data[0:2]))
        # user.test_id = 1
        user.spd.age = int(form.number.data[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res == 'success':
            login_user(user)
            # return redirect(url_for('helper.get_grade_start', num=user.user_number))
            # if request.args.get('next'):
            #     next = url_for('main.index')+request.args.get('next')
            #     print(next)

            return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
        else:
            flash(login_res)
    return render_template('helper/wechat_login.html', form=form, message=current_app.config['REMEMBER_PASSWORD_MESSAGE'])


@helper.route('/wechat/cal')
def get_wechat_cal_start():
    openid = request.args.get('openid')
    if not openid:
        return redirect(url_for('helper.grade_cal',term=1))
    else:
        user = User.query.filter_by(wechat_id=openid).first()
        if user is None or user.wechat_id is None:
            return redirect(url_for('helper.jw_wechat_login', openid=openid))
        try:
            current_app.logger.info('%s %s cal' % (openid, user.user_number))
            pwd = user.password
            cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
            pwd = cipher.decrypt(pwd)
        except:
            return redirect(url_for('helper.jw_wechat_login', openid=openid))

        data = {
            'userName': user.user_number,
            'password': pwd
        }
        user.spd = jw_spider()
        user.spd.site = 0
        user.spd.age = int(user.user_number[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res == 'success':
            login_user(user)
            # return redirect(url_for('helper.get_grade_start', num=user.user_number))
            # if request.args.get('next'):
            #     next = url_for('main.index')+request.args.get('next')
            #     print(next)

            return redirect(request.args.get('next') or url_for('helper.grade_cal'))
        else:
            user.spd.site = 1
            login_res = user.spd.login(login_data=data)
            if login_res == 'success':
                login_user(user)
                return redirect(request.args.get('next') or url_for('helper.grade_cal'))
            else:
                return redirect(url_for('helper.jw_wechat_login', type=1, openid=openid))


@helper.route('/wechat/timetable')
def get_wechat_timetable_start():
    openid = request.args.get('openid')
    week_now = datetime.datetime.now().isocalendar()[1] - current_app.config.get("STRAT_WEEK", 6)
    # 当前是第几周

    current_app.logger.info("week_now is %d" % week_now)
    # week_now = 1
    if not openid:
        return redirect(url_for('helper.timetable',week=week_now))
        ##当前周
    else:
        user = User.query.filter_by(wechat_id=openid).first()
        if user is None or user.wechat_id is None:
            return redirect(url_for('helper.jw_wechat_login', openid=openid, next=url_for('helper.get_wechat_timetable_start')))
        login_user(user)
        if not user.remember_me:
            user.create_spd()
            return redirect(url_for('helper.timetable', week=week_now))
        try:
            current_app.logger.info('%s %s timetable' % (openid, user.user_number))
            pwd = user.password
            cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
            pwd = cipher.decrypt(pwd)
        except:
            return redirect(url_for('helper.jw_wechat_login', openid=openid, next=url_for('helper.get_wechat_timetable_start')))

        data = {
            'userName': user.user_number,
            'password': pwd
        }
        user.spd = jw_spider()
        user.spd.site = 0
        user.spd.age = int(user.user_number[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res != 'success':
            user.spd.site = 1
            login_res = user.spd.login(login_data=data)
            if login_res != 'success':
                print(login_res)
                flash(login_res)

            # return redirect(url_for('helper.jw_wechat_login', type=1, openid=openid,
            # next=url_for('helper.get_wechat_timetable_start')))

        return redirect(url_for('helper.timetable', week=week_now))


@helper.route('/wechat/cal_click')
def wechat_cal_click():
    code = request.args.get('code')
    if not code:
        current_app.logger.info('test1')
        return redirect(url_for('helper.get_wechat_cal_start'))
    else:
        current_app.logger.info(current_user.is_authenticated)
        req_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
            current_app.config['APP_ID'], current_app.config['APP_SECRET'], code)
        res = requests.get(req_url).content
        res = res.decode()
        openid = json.loads(res).get('openid')
        return redirect(url_for('helper.get_wechat_cal_start', openid=openid))


@helper.route('/wechat/grade_click')
def wechat_grade_click():
    code = request.args.get('code')
    if not code:
        current_app.logger.info('test1')
        return redirect(url_for('helper.get_wechat_grade_start'))
    else:
        current_app.logger.info(current_user.is_authenticated)
        req_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
            current_app.config['APP_ID'], current_app.config['APP_SECRET'], code)
        res = requests.get(req_url).content
        res = res.decode()
        openid = json.loads(res).get('openid')
        return redirect(url_for('helper.get_wechat_grade_start', openid=openid))


@helper.route('/wechat/timetable_click')
def wechat_timetable_click():
    code = request.args.get('code')
    if not code:
        current_app.logger.info('test1')
        return redirect(url_for('helper.get_wechat_timetable_start'))
    else:
        current_app.logger.info(current_user.is_authenticated)
        req_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
            current_app.config['APP_ID'], current_app.config['APP_SECRET'], code)
        res = requests.get(req_url).content
        res = res.decode()
        openid = json.loads(res).get('openid')
        return redirect(url_for('helper.get_wechat_timetable_start', openid=openid))


@helper.route('/timetable')
@jw_login_required
def timetable_start():
    return redirect(url_for('helper.timetable', week=1))


@helper.route('/timetable/<int:week>')
def timetable(week=1):
    if not current_user.is_authenticated:
        return redirect(url_for('helper.jw_login', next=url_for('helper.timetable', week=week)))
    if not current_user.remember_me:
        try:
            res = current_user.spd.get_course()
            current_app.logger.info(res)
            if res ==[]:
                if current_user.wechat_id:
                    return redirect(url_for('helper.jw_wechat_login', openid=current_user.wechat_id, next=url_for('helper.timetable', week=week)))
                else:
                    return redirect(url_for('helper.jw_login', next=url_for('helper.timetable', week=week)))
        except:
            return redirect(url_for('helper.jw_wechat_login', openid=current_user.wechat_id, next=url_for('helper.timetable', week=week)))
    else:
        res = current_user.get_courses_from_database()
        if res == []:
            res = current_user.spd.get_course()
            if res == []:
                flash('获取课程失败')
                return redirect(url_for('helper.jw_wechat_login', openid=current_user.wechat_id, next=url_for('helper.get_wechat_timetable_start')))
            current_user.save_courses_into_database(res, stu=current_user._get_current_object())
    # res = current_user.spd.get_course()

    # res=[['毛泽东思想和中国特色社会主义理论体系概论（理论部分）', '高静', '周二 第5-7节 1-18周 仙Ⅱ-314', '00000030A'],
    #  ['现代气候学基础', '陈星, 张录军, 黄樱', '周三 第3-4节 1-14周  仙Ⅱ-314\n周五 第3-4节 1-14周  仙Ⅱ-314', '17010040'],
    #  ['数值天气预报', '孙旭光, 杨修群', '周三 第1-2节 双周 丙502.506\n周三 第1-2节 单周 仙Ⅱ-314\n周一 第3-4节 1-18周 仙Ⅱ-314', '17010060'],
    #  ['气象统计预报', '汤剑平, 宋金杰', '周一 第3-4节 1-18周 仙Ⅱ-314\n周五 第1-2节 双周 丙502.506\n周五 第1-2节 单周 仙Ⅱ-314', '17010070'],
    #  ['天气分析与预报技术', '王亦平', '周三 第5-8节 1-15周  预报台\n周四 第1-4节 1-15周  预报台', '17010150'], ['123', '王', '周五 第9-11节 1-15周  预报台\n周五 第9-11节 1-15周  预报台', '17010150']]
    # random.shuffle(color_list)
    courses = current_user.spd.create_courses(week=week, course_result=res)[0]
    courses_except = current_user.spd.create_courses(week=week, course_result=res)[1]
    for r in res:
        r[2] = r[2].replace('\n', '<br>')
    color_list = ['#29B6F6', '#9CCC65', '#EC407A', '#FFA726', '#AB47BC', '#FF7043',
                  '#7E57C2', '#26C6DA', '#66BB6A', '#8D6E63', '#42A5F5', '#BDBDBD', '#5C6BC0', '#26A69A', '#ef5350', '#D4E157']
    return render_template('helper/course.html', courses=courses, week_now=week, color_list=color_list, msg=res, len=len, courses_except=courses_except)


@helper.route('/suggestion', methods=['GET', 'POST'])
def suggest():
    form = suggestForm()
    if form.validate_on_submit():
        content = form.suggestion.data
        openid = request.args.get('openid')
        if not openid:
            openid = 'Someone'
        send_email_by_suggestion('mail/suggestion', wechat_id=openid, content=content)
        flash('已收到您的反馈！')
    return render_template('helper/suggestion.html', form=form)
