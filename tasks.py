# coding: utf-8
import os
import json
import datetime
import requests
from flask import current_app
from wechat_sdk.exceptions import OfficialAPIError

from app import redis
from app.main.wechat import init_wechat_sdk
from app.models import User
from manage import celery


@celery.task(name="send_timetable")
def send_timetable():
    if has_disable_send_timetable():  # 可以通过配置文件来禁用课表通知
        current_app.logger.info("has disable send timetable!")
        return

    wechat = init_wechat_sdk()
    template_id = current_app.config.get("SEND_TIMETABLE_TEMPLATE_ID")

    cur_week = get_cur_week()
    cur_day = get_cur_day()

    users = redis.smembers("subscribe_timetable")

    if users:  # 如果有人订阅了成绩通知才去获取天气信息
        weather = get_weather_info()

    for openid in users:
        user = User.query.filter_by(wechat_id=openid).first()
        if not user or not user.password:
            redis.srem(openid, 1)
            continue

        courses = get_today_courses(user, cur_day, cur_week)
        if not courses:
            continue

        msg_data = get_msg_data(courses)

        if weather:
            msg_data['head']['value'] += u'\n今日天气：' + weather

        url = current_app.config.get("SITE_URL") + "/timetable/" + str(cur_week)
        try:
            wechat.send_template_message(openid.decode("ascii"), template_id,
                                         msg_data, url=url)
        except OfficialAPIError as e:
            current_app.logger.error("OfficialAPIError: " + str(e.errcode) + ": " + e.errmsg)

    return len(users)


def has_disable_send_timetable():
    if os.path.exists("config.json"):
        with open("config.json") as f:
            conf = json.load(f)
            return conf.get("disable_send_timetable", False)
    return False


def get_cur_day():
    """
    根据配置文件以及当前日期来判断上哪一天的课程
    """
    day_now = datetime.datetime.now().isocalendar()[2] - 1
    if os.path.exists("config.json"):
        with open("config.json") as f:
            conf = json.load(f)
            day_now = conf.get("day_now", day_now)

    return day_now


def get_cur_week():
    """
    根据配置文件以及当前日期来判断上哪一周的课程
    """
    week_now = datetime.datetime.now().isocalendar()[1] - current_app.config.get("STRAT_WEEK", 6)
    if os.path.exists("config.json"):
        with open("config.json") as f:
            conf = json.load(f)

            week_now = conf.get("week_now", week_now)

    return week_now


def get_today_courses(user, day_now, week_now):
    res = user.get_courses_from_database()
    if not res:
        res = user.spd.get_course()
    if not res:
        return
    else:
        # courses_raw 是一天内所有课程的原始数据
        courses_raw = user.spd.create_courses(week=week_now, course_result=res)[0][day_now]
        courses = {}
        for index, item in enumerate(courses_raw):
            if not item[0] or not item[1]:  # 没有课
                continue
            course_index = item[1][0]

            if course_index not in courses:
                courses[course_index] = [index + 1, item[0], 0]
            else:
                courses[course_index][2] += 1
                if not courses[course_index][1].endswith(" "):  # 只保留课程名+上课教室
                    courses[course_index][1] += (" " + item[0] + " ")
            # courses的一项：<课程序号, [课程时间，课程名+上课教室, 课程时长]>

        return courses


def get_msg_data(courses):
    data = {
        "head": {"value": "早上好！", "color": "#000000"},
        "morning": {"value": "", "color": "#173177"},
        "afternoon": {"value": "", "color": "#173177"},
        "night": {"value": "", "color": "#173177"},
        "tail": {"value": "再见！", "color": "#000000"}
    }

    # 课程信息填充到data里面
    for one_course in courses.values():
        course_time = one_course[0]
        course_info = one_course[1] + str(one_course[0]) + "-" + str(one_course[2] + one_course[0]) + "节\t"
        # course_info: 课程名 上课教室 开始节数-结束节数

        if course_time <= 4:
            data['morning']['value'] += course_info
        elif course_time <= 8:
            data['afternoon']['value'] += course_info
        else:
            data['night']['value'] += course_info

    # 处理没课的时间段
    for key in list(data.keys())[1:-1]:  # 只考虑中间三条信息
        if not data[key]["value"]:
            data[key]['value'] = "没有."
        else:
            data[key]['value'] = data[key]['value'].strip() + '.'

    return data


def get_weather_info():
    # api信息： https://www.nowapi.com/api/weather.future
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    appkey = "25438"  # API
    sign = "89515add40ab3eb11550e099d7e234e8"
    weather_url = "http://api.k780.com/?app=weather.future&weaid=nanjing&appkey={0}&sign={1}&format=json".format(
        appkey, sign)
    aqi_url = "http://api.k780.com/?app=weather.pm25&weaid=nanjing&appkey={0}&sign={1}&format=json".format(
        appkey, sign)
    result = None

    try:
        rsp = requests.get(weather_url)
        text = rsp.json()
        w = text['result'][0]  # 今日天气信息
        rsp = requests.get(aqi_url)
        text = rsp.json()
        a = text['result']

        text = w['weather'] + "，"
        temperature = w['temp_low'] + u"-" + w['temp_high'] + "℃，"
        wind = w["wind"] + w['winp'] + "。\n"

        aqi = u"空气质量：" + a['aqi_levnm'] + "，AQI指数为" + a['aqi']

        result = text + temperature + wind + aqi + "。"
    except Exception as e:
        current_app.logger.error(e)
    finally:
        return result


@celery.task(name="send_grade")
def send_grade():
    if has_disable_send_grade():  # 可以通过配置文件来关掉成绩通知
        current_app.logger.info("has disable send grade!")
        return 0

    wechat = init_wechat_sdk()
    template_id = current_app.config.get("SEND_GRADE_TEMPLATE_ID")
    users = redis.hgetall("subscribe_grade")

    for openid, info in users.items():
        user = User.query.filter_by(wechat_id=openid).first()
        if not user or not user.password:
            redis.hdel("subscribe_grade", openid)
            continue

        info = info.decode('utf-8').split()  # info的格式：cur_term 已有成绩的课程名+
        cur_term = int(info[0]) - 1  # 当前学期
        old_grades = info[1:]

        grades = get_grade(user, old_grades, cur_term)

        # 如果没有新成绩
        if not grades:
            continue

        msg_data = get_grade_msg(grades)

        save_new_grade(info, openid, grades)

        url = current_app.config.get("SITE_URL") + "/grades/" + str(cur_term)

        try:
            wechat.send_template_message(openid.decode("ascii"), template_id,
                                         msg_data, url=url)
        except OfficialAPIError as e:
            current_app.logger.error("OfficialAPIError: " + str(e.errcode) + ": " + e.errmsg)

    return len(users)


def has_disable_send_grade():
    if os.path.exists("config.json"):
        with open("config.json") as f:
            conf = json.load(f)
            return conf.get("disable_send_grade", False)
    return False


def get_grade(user, old_grades, cur_term):
    """
    从教务网获取当前成绩并返回有新成绩的课程
    """
    result = None
    try:
        grades = user.spd.get_grade(age=user.spd.age, term=cur_term)
        result = []

        for item in grades:
            if item[0] not in old_grades:
                result.append(item)

    except Exception as e:
        current_app.logger.error(e)
    finally:
        return result


def get_grade_msg(grades):
    data = {
        "head": {"value": "", "color": "#000000"},
        "msg": {"value": "", "color": "#173177"},
        "tail": {"value": "", "color": "#000000"}
    }
    values = []
    for grade in grades:
        values.append(grade[0] + "：" + grade[2] + "学分，成绩：" + grade[3] + "。")

    data['msg']['value'] = "\n".join(values)

    return data


def save_new_grade(info, openid, new_grades):
    """
    将现在所有有成绩的课程都记录下来
    """
    for item in new_grades:
        info.append(item[0])
    info_str = " ".join(info)
    redis.hset("subscribe_grade", openid, info_str)
