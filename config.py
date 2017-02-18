#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WXAESKEY =  os.environ.get('WXAESKEY')
    APP_ID =  os.environ.get('APP_ID')
    APP_SECRET =  os.environ.get('APP_SECRET')
    TOKEN =  os.environ.get('TOKEN')
    PASSWORD_SECRET_KEY =  os.environ.get('PASSWORD_SECRET_KEY')
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    SEND_MAIL_TO = 'njuexciting@163.com'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'njuexciting@163.com'
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # FLASKY_POSTS_PER_PAGE = 20
    # FLASKY_FOLLOWERS_PER_PAGE = 50
    # FLASKY_COMMENTS_PER_PAGE = 30
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
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=http%3A%2F%2Fgreatnju.com%2Fwechat%2Fgrade_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    },
                    {
                        "type": 'view',
                        "name": "GPA计算",
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=http%3A%2F%2Fgreatnju.com%2Fwechat%2Fcal_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    },
                    {
                        "type": 'view',
                        "name": "我的课表",
                        "url": 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s' % APP_ID + '&redirect_uri=http%3A%2F%2Fgreatnju.com%2Fwechat%2Ftimetable_click&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
                    }
                    # {
                    #     "type": 'view',
                    #     "name": '???',
                    #     "url": 'http://www.baidu.com'
                    # }
                ]
            },
            {
                "type": 'view',
                "name": "使用帮助",
                "url": 'http://www.qq.com'
            },
            {
                'type': 'click',
                'name': '联系我们',
                'key': 'contact'
            }
        ]
    }

    WELCOME_TEXT = u"欢迎关注NJU小帮手，一起搞个大新闻\n"

    WAIT_FOR_DEV_TEXT = u"此功能正在开发中，请耐心等待"

    COMMAND_TEXT = u""
    # COMMAND_TEXT = u"请回复以下关键词开始：\n成绩\ngpa\n课程\n"

    COMMAND_NOT_FOUND_TEXT = u"收到你的留言啦！"

    REMEMBER_PASSWORD_MESSAGE = u"选择将您的微信号与教务系统账号绑定后，今后使用成绩查询、GPA计算、课程表等功能时将无需再次登录。为此，我们将以某种形式储存您的教务系统密码。我们承诺绝不将您的信息用作其其他用途，并妥善保管您的信息。"

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
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



