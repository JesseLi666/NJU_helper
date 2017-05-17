#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from celery.schedules import crontab
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 微信相关的配置
    WXAESKEY = os.environ.get('WXAESKEY')
    APP_ID = os.environ.get('APP_ID')
    APP_SECRET = os.environ.get('APP_SECRET')
    TOKEN = os.environ.get('TOKEN')

    # 对用户密码加密的秘钥
    PASSWORD_SECRET_KEY = os.environ.get('PASSWORD_SECRET_KEY')

    # 邮件相关的配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    SEND_MAIL_TO = 'njuexciting@163.com'
    FLASKY_MAIL_SENDER = 'njuexciting@163.com'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # celery 相关的配置
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Shanghai'

    # celery 定时任务
    CELERYBEAT_SCHEDULE = {
        'send_grade_task': {
            'task': 'send_grade',
            'schedule': crontab(hour='7-23/3')  # 7-23点，每三个小时执行一次
        },
        'send_timetable_task': {
            'task': 'send_timetable',
            'schedule': crontab(minute=20, hour=7)  # 每天 7:20 执行一次
        }
    }

    # 本学期起始周数
    START_WEEK = 6

    # 微信模板消息的id
    SEND_TIMETABLE_TEMPLATE_ID = ""
    SEND_GRADE_TEMPLATE_ID = ""

    # 部署网站的URL
    SITE_URL = "http://greatnju.com"

    JW_BASE_URL = ['http://jw.nju.edu.cn:8080/jiaowu/',
                   'http://219.219.120.48/jiaowu/']

    MENU_SETTING = {
        "button": [
            {
                'name': '教务助手',
                'sub_button': [
                    {
                        "type": 'view',
                        "name": "成绩查询",
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=' + SITE_URL + '/wechat/grade_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    },
                    {
                        "type": 'view',
                        "name": "GPA计算",
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=' + SITE_URL + '/wechat/cal_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    },
                    {
                        "type": 'view',
                        "name": "我的课表",
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=' + SITE_URL + '/wechat/timetable_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    }
                ]
            },
            {
                "type": 'view',
                "name": "使用帮助",
                "url": 'http://mp.weixin.qq.com/s/8iWO72QNAuhqS7pjgwFMLw'
            },
            {
                'type': 'view',
                'name': '联系我们',
                'url': 'https://jq.qq.com/?_wv=1027&k=453dRgc'
            }
        ]
    }

    WELCOME_TEXT = u"*罒▽罒*yaho!\n欢迎关注NJU小帮手，一起搞个大新闻!\n\n"

    WAIT_FOR_DEV_TEXT = u"此功能正在开发中，请耐心等待"

    # COMMAND_TEXT = u""
    COMMAND_TEXT = u"(❁´︶`❁)请点击最下方菜单或者回复以下关键词开始：\n\n  成绩\n  gpa\n  课表\n\n目前教务系统连接不稳定，小帮手部分功能可能无法正常使用"

    COMMAND_NOT_FOUND_TEXT = u"收到你的留言啦！"

    REMEMBER_PASSWORD_MESSAGE = u"选择将您的微信号与教务系统账号绑定后，今后使用成绩查询、GPA计算、课程表等功能时将无需再次登录。为此，我们将以某种形式储存您的教务系统密码。我们承诺绝不将您的信息用作其他用途，并妥善保管您的信息。"


class DevelopmentConfig(Config):
    # DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
