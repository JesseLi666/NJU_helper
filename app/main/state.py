import datetime

from flask import current_app

from .. import redis
from ..models import AESCipher, User


def set_user_state(openid, state):
    """设置用户状态"""
    redis.hset('wechat:user:' + openid, 'state', state)
    return None


def get_user_state(openid):
    """获取用户状态"""
    return redis.hget('wechat:user:' + openid, 'state')


def set_user_last_interact_time(openid, timestamp):
    """保存最后一次交互时间"""
    redis.hset('wechat:user:' + openid, 'last_interact_time', timestamp)
    return None


def get_user_last_interact_time(openid):
    """获取最后一次交互时间"""
    last_time = redis.hget('wechat:user:' + openid, 'last_interact_time')
    if last_time:
        return last_time
    else:
        return 0


def jw_delete(id):
    user = User.query.filter_by(wechat_id=id).first()
    if user is None or user.password is None:
        msg = '未绑定教务账号'
    else:
        user.delete_password()
        msg = '取消绑定成功'
    return msg


def courses_fresh(id):
    user = User.query.filter_by(wechat_id=id).first()
    if user is None or user.password is None:
        msg = '未绑定教务账号'
    else:
        pwd = user.password
        cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
        pwd = cipher.decrypt(pwd)
        data = {
            'userName': user.user_number,
            'password': pwd
        }
        user.create_spd()
        user.spd.site = 0
        user.spd.age = int(user.user_number[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res != 'success':
            user.spd.site = 1
            login_res = user.spd.login(login_data=data)
            if login_res != 'success':
                msg = '登陆教务系统失败'
                return msg
        res = user.spd.get_course()
        if res == []:
            msg = '获取课程失败'
            return msg
        user.save_courses_into_database(res, stu=user)
        msg = '刷新课程成功'
    return msg
