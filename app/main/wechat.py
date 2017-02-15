from wechat_sdk import WechatBasic, WechatConf
from wechat_sdk.messages import TextMessage, ImageMessage, EventMessage
from .. import redis
from flask import current_app, logging
import re
import urllib.parse
from .state import jw_delete, courses_fresh
# from .state import set_user_state, get_user_state, set_user_last_interact_time, get_user_last_interact_time

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
        # jsapi_ticket = wechat.get_jsapi_ticket()
        # redis.set("wechat:jsapi_ticket", jsapi_ticket['jsapi_ticket'], 7000)
        # redis.set("wechat:jsapi_ticket_expires_at",
        #           jsapi_ticket['jsapi_ticket_expires_at'], 7000)

    return wechat

def update_wechat_token():
    """刷新微信 token """
    # wechat = init_wechat_sdk()
    wechat.grant_token()
    # wechat.grant_jsapi_ticket()
    access_token = wechat.get_access_token()
    redis.set("wechat:access_token", access_token['access_token'], 7000)
    redis.set("wechat:access_token_expires_at",
              access_token['access_token_expires_at'], 7000)
    return wechat.response_text('Done!')
    # jsapi_ticket = wechat.get_jsapi_ticket()
    # redis.set("wechat:jsapi_ticket", jsapi_ticket['jsapi_ticket'], 7000)
    # redis.set("wechat:jsapi_ticket_expires_at",
    #           jsapi_ticket['jsapi_ticket_expires_at'], 7000)

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
    #.parse_data(data, msg_signature=None, timestamp=None, nonce=None)
    wechat.parse_data(data=data, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
    #公共信息获取
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
        u'刷新accesstoken':update_wechat_token,
        u'更新菜单': update_menu_setting,
        #why u
        u'成绩|成绩查询|查成绩':grade_reply,
        u'计算|GPA|gpa|计算器|学分绩':cal_reply,
        u'课表|课程|我的课表|课程表':timetable_reply,
        u'取消绑定':jw_cancel,
        u'刷新课程':course_fresh
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
        'cal': cal_click
    }
    # 匹配指令后，重置状态
    # set_user_state(openid, 'default')
    response = commands[message.key]()
    return response

@set_msg_type('subscribe')
def subscribe_resp():
    """订阅类型回复"""
    # set_user_state(openid, 'default')
    response = subscribe()
    return response

@set_msg_type('view')
def subscribe_resp():
    """菜单跳转类型回复"""
    # set_user_state(openid, 'default')
    # response = subscribe()
    content = '菜单跳转'
    response = wechat.response_text(content)
    return response

def grade_reply():
    url = 'http://www.greatnju.com/wechat/grade'
    data = {'openid': openid}
    url = url + '?'+urllib.parse.urlencode(data)
    articles = [{
        'title': u'成绩查询',
        'description': u'点击查询成绩',
        'url': url
    }]
    return wechat.response_news(articles=articles)

def cal_reply():
    url = 'http://www.greatnju.com/wechat/cal'
    data = {'openid': openid}
    url = url + '?'+urllib.parse.urlencode(data)
    articles = [{
        'title': u'GPA计算器',
        'description': u'点击计算GPA',
        'url': url
    }]
    return wechat.response_news(articles=articles)

def timetable_reply():
    url = 'http://www.greatnju.com/wechat/timetable'
    data = {'openid': openid}
    url = url + '?'+urllib.parse.urlencode(data)
    articles = [{
        'title': u'我的课表',
        'description': u'点击查看课表',
        'url': url
    }]
    return wechat.response_news(articles=articles)

def update_menu_setting():
    """更新自定义菜单"""
    # logging.info('?')
    current_app.logger.info('test')
    # current_app.logger.info(current_app.config['MENU_SETTING'])
    try:
        wechat.create_menu(current_app.config['MENU_SETTING'])
        # print(current_app.config['MENU_SETTING'])
        # logging.info(current_app.config['MENU_SETTING'])
        current_app.logger.info('1')
    except Exception as e:
        current_app.logger.info('2')
        return wechat.response_text(e)
    else:
        current_app.logger.info('3')
        return wechat.response_text('Done!')

def subscribe():
    """回复订阅事件"""
    content = current_app.config['WELCOME_TEXT'] + current_app.config['COMMAND_TEXT']
    return wechat.response_text(content)

def score_click():
    msg = '请回复‘成绩’'
    return wechat.response_text(msg)


def cal_click():
    msg = '请回复‘计算’'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx9fc2c855d6d9ddb4&redirect_uri=http%3A%2F%2Fwww.greatnju.com%2Fwechat%2Fcal_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
    return wechat.response_text(msg)

def jw_cancel():
    return wechat.response_text(jw_delete(openid))

def course_fresh():
    return wechat.response_text(courses_fresh(openid))
