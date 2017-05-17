# coding: utf-8
from wechat_sdk import WechatBasic, WechatConf
from wechat_sdk.messages import TextMessage, ImageMessage, EventMessage
import datetime
import re
import urllib.parse

from flask import current_app, logging

from app import redis
from app.main.state import jw_delete, courses_fresh
from app.models import User


def init_wechat_sdk():
    """初始化微信 SDK"""
    access_token = redis.get("wechat:access_token")
    # jsapi_ticket = redis.get("wechat:jsapi_ticket")
    token_expires_at = redis.get("wechat:access_token_expires_at")
    # ticket_expires_at = redis.get("wechat:jsapi_ticket_expires_at")
    # if access_token and jsapi_ticket and token_expires_at and ticket_expires_at:
    if access_token and token_expires_at:
        conf = WechatConf(
            appid=current_app.config['APP_ID'],
            appsecret=current_app.config['APP_SECRET'],
            token=current_app.config['TOKEN'],
            access_token=access_token,
            encrypt_mode='normal',
            access_token_expires_at=int(token_expires_at)

        )
        wechat = WechatBasic(conf=conf)
    else:
        conf = WechatConf(
            appid=current_app.config['APP_ID'],
            appsecret=current_app.config['APP_SECRET'],
            encrypt_mode='normal',
            token=current_app.config['TOKEN']
        )
        wechat = WechatBasic(conf=conf)
        access_token = wechat.get_access_token()
        redis.set("wechat:access_token", access_token['access_token'], 7000)
        redis.set("wechat:access_token_expires_at",
                  access_token['access_token_expires_at'], 7000)

    return wechat


def update_wechat_token():
    """刷新微信 token """
    wechat.grant_token()
    access_token = wechat.get_access_token()
    redis.set("wechat:access_token", access_token['access_token'], 7000)
    redis.set("wechat:access_token_expires_at",
              access_token['access_token_expires_at'], 7000)
    return wechat.response_text('Done!')


def get_wechat_access_token():
    """获取 access_token"""
    access_token = redis.get("wechat:access_token")
    if access_token:
        return access_token
    else:
        current_app.logger.warning(u"获取 access_token 缓存失败")
        return None


def wechat_response(data, msg_signature=None, timestamp=None, nonce=None):
    global message, openid, wechat
    wechat = init_wechat_sdk()
    wechat.parse_data(data=data, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
    # 公共信息获取
    id = wechat.message.id  # 对应于 XML 中的 MsgId
    target = wechat.message.target  # 对应于 XML 中的 ToUserName
    source = wechat.message.source  # 对应于 XML 中的 FromUserName
    time = wechat.message.time  # 对应于 XML 中的 CreateTime
    type = wechat.message.type  # 对应于 XML 中的 MsgType
    raw = wechat.message.raw  # 原始 XML 文本，方便进行其他分析
    #用户信息写入数据库###
    # set_user_info(openid)
    message = wechat.get_message()
    openid = message.source
    try:
        get_resp_func = msg_type_resp[message.type]
        response = get_resp_func()
    except KeyError:
        # 默认回复微信消息
        response = 'success'
    # 保存最后一次交互的时间
    # set_user_last_interact_time(openid, message.time)
    return response


# 储存微信消息类型所对应函数（方法）的字典
msg_type_resp = {}


def set_msg_type(msg_type):
    """
    储存微信消息类型所对应函数（方法）的装饰器
    """
    def decorator(func):
        msg_type_resp[msg_type] = func
        return func
    return decorator


@set_msg_type('text')
def text_resp():
    """文本类型回复"""
    # 默认回复微信消息
    response = 'success'
    # 替换全角空格为半角空格
    message.content = message.content.replace(u'　', ' ')
    # 清除行首空格
    message.content = message.content.lstrip()
    # 指令列表
    commands = {
        # u'取消': cancel_command,
        # u'^\?|^？': all_command,
        # u'^雷达|^雷達': weather_radar,
        # u'^電話|^电话': phone_number,
        # u'^公交|^公车|^公車': bus_routes,
        # u'^放假|^校历|^校曆|^校歷': academic_calendar,
        # u'合作': contact_us,
        # u'明信片': postcard,
        # u'^游戏|^遊戲': html5_games,
        # u'^成绩|^成績|^补考|^補考': exam_grade,
        # u'^新闻|^新聞': get_school_news,
        # u'^天气|^天氣': get_weather_news,
        # u'陪聊': enter_chat_state,
        # u'^四级|^六级|^四六级|^四級|^六級|^四六級': cet_score,
        # u'^图书馆|^找书|^圖書館|^找書': search_books,
        # u'^借书|^借書': borrowing_record,
        # u'^续借|^續借': renew_books,
        # u'^签到|^起床|^簽到': daily_sign,
        # u'^音乐|^音樂': play_music,
        # u'^论坛|^論壇': bbs_url,
        # u'^快递|^快遞': enter_express_state,
        # u'^绑定|^綁定': auth_url,
        u'刷新accesstoken': update_wechat_token,
        u'更新菜单': update_menu_setting,
        # why u
        u'成绩|成绩查询|查成绩': grade_reply,
        u'计算|GPA|gpa|计算器|学分绩': cal_reply,
        u'课表|课程|我的课表|课程表': timetable_reply,
        u'取消绑定': jw_cancel,
        u'刷新课程': course_fresh,
        u'订阅课表': subscribe_timetable,
        u'退订课表': unsubscribe_timetable,
        u'订阅成绩': subscribe_grade,
        u'退订成绩': unsubscribe_grade
    }
    # 状态列表
    state_commands = {
        # 'chat': chat_robot,
        # 'express': express_shipment_tracking
    }
    # 匹配指令
    command_match = False
    for key_word in commands:
        if re.match(key_word, message.content):
            # 指令匹配后，设置默认状态
            # set_user_state(openid, 'default')
            response = commands[key_word]()
            command_match = True
            break
    if not command_match:
        # 匹配状态
        content = current_app.config['COMMAND_NOT_FOUND_TEXT']
        response = wechat.response_text(content)
        # state = get_user_state(openid)
        # # 关键词、状态都不匹配，缺省回复
        # if state == 'default' or not state:
        #     response = command_not_found()
        # else:
        #     response = state_commands[state]()
    return response


@set_msg_type('click')
def click_resp():
    """菜单点击类型回复"""
    commands = {
        # 'phone_number': phone_number,
        # 'express': enter_express_state,
        # 'score': exam_grade,
        # 'borrowing_record': borrowing_record,
        # 'renew_books': renew_books,
        # 'sign': daily_sign,
        # 'chat_robot': enter_chat_state,
        # 'music': play_music,
        # 'weather': get_weather_news
        'score': score_click,
        'cal': cal_click,
        'contact': contact_click,
    }
    # 匹配指令后，重置状态
    # set_user_state(openid, 'default')
    response = commands[message.key]()
    return response


@set_msg_type('subscribe')
def subscribe_resp():
    """订阅类型回复"""
    response = subscribe()
    return response


@set_msg_type('view')
def subscribe_resp():
    """菜单跳转类型回复"""
    content = '菜单跳转'
    response = wechat.response_text(content)
    return response


def grade_reply():
    url = current_app.config['SITE_URL'] + '/wechat/grade'
    data = {'openid': openid}
    url = url + '?' + urllib.parse.urlencode(data)
    articles = [{
        'title': u'成绩查询',
        'description': u'点击查询成绩',
        'url': url
    }]
    return wechat.response_news(articles=articles)


def cal_reply():
    url = current_app.config['SITE_URL'] + '/wechat/cal'
    data = {'openid': openid}
    url = url + '?' + urllib.parse.urlencode(data)
    articles = [{
        'title': u'GPA计算器',
        'description': u'点击计算GPA',
        'url': url
    }]
    return wechat.response_news(articles=articles)


def timetable_reply():
    url = current_app.config['SITE_URL'] + '/wechat/timetable'
    data = {'openid': openid}
    url = url + '?' + urllib.parse.urlencode(data)
    articles = [{
        'title': u'我的课表',
        'description': u'点击查看课表',
        'url': url
    }]
    return wechat.response_news(articles=articles)


def update_menu_setting():
    """更新自定义菜单"""
    try:
        wechat.create_menu(current_app.config['MENU_SETTING'])
    except Exception as e:
        return wechat.response_text(e)
    else:
        return wechat.response_text('Done!')


def subscribe():
    """回复订阅事件"""
    content = current_app.config['WELCOME_TEXT'] + current_app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def score_click():
    msg = '请回复‘成绩’'
    return wechat.response_text(msg)


def contact_click():
    msg = '点击链接加入群【NJU小帮手的小帮手们】：https://jq.qq.com/?_wv=1027&k=453dRgc'
    return wechat.response_text(msg)


def cal_click():
    msg = '请回复‘计算’'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx9fc2c855d6d9ddb4&redirect_uri=' + \
        current_app.config['SITE_URL'] + \
        '/wechat/cal_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
    return wechat.response_text(msg)


def jw_cancel():
    return wechat.response_text(jw_delete(openid))


def course_fresh():
    return wechat.response_text(courses_fresh(openid))


def subscribe_timetable():  # 保存在redis的集合subscribe_timetable中
    user = User.query.filter_by(wechat_id=openid).first()
    if user is None or user.password is None:
        msg = '未绑定教务账号'
    else:
        redis.sadd("subscribe_timetable", openid)
        msg = '订阅课表成功'
    return wechat.response_text(msg)


def unsubscribe_timetable():
    res = redis.srem("subscribe_timetable", openid)
    if res == 1:
        return wechat.response_text("退订成功")
    return wechat.response_text("未订阅课表")


def subscribe_grade():  # 保存在redis的字典subscribe_grade中
    user = User.query.filter_by(wechat_id=openid).first()
    if user is None or user.password is None:
        msg = '未绑定教务账号'
    else:
        # 先获取当前以有成绩的课程，并且记录下来
        cur_year = datetime.datetime.now().year % 2000
        cur_term = total_term = (cur_year - user.spd.age) * 2
        grade_res = user.spd.get_grade(age=user.spd.age, term=cur_term)
        # grade_res 是当前学期已经有成绩的所有课程列表，每一项的格式为：[课程名, 类型，学分，成绩]
        # 记录当前学期，不用每次都计算
        value = str(cur_term) + " "
        for item in grade_res:
            value += (item[0]) + " "  # 只记录课程名
        redis.hsetnx("subscribe_grade", openid, value)
        msg = '订阅成绩成功'
    return wechat.response_text(msg)


def unsubscribe_grade():
    res = redis.hdel("subscribe_grade", openid)
    if res == 1:
        return wechat.response_text("退订成功")
    return wechat.response_text("未订阅成绩")


from app.main import main as main_blueprint


@main_blueprint.app_errorhandler(Exception)
def exception_handler(e):
    """
    拦截应用中出现的错误，返回提示信息并发送邮件给管理员
    """
    from app.helper.mail import send_email_by_error
    from flask import request
    import traceback

    # 从异常中获取堆栈信息
    try:
        raise e
    except Exception as e:
        error_msg = traceback.format_exc()
        current_app.logger.error(error_msg)
    msg = """
    openid: {0}\n
    url: {1}\n
    method: {2}\n
    message: {3}\n
    traceback: {4}\n
    """

    wechat_message = message.content if message.type == "text" else message.type

    msg = msg.format(openid, request.url, request.method, wechat_message, error_msg)

    try:
        send_email_by_error(msg)
    except Exception as e:
        current_app.logger.error(e)
    return wechat.response_text("非常抱歉，公众号后台出现了未知的错误，我们会尽快修复！")
