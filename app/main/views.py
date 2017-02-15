from flask import render_template, request, make_response, current_app, redirect, url_for, flash
from flask_login import login_user
from . import main
import hashlib
from .wechat import init_wechat_sdk, wechat_response
import os
# from ..models import User, AESCipher
# from .. import db
# from ..helper.forms import wechat_JWLoginForm
# from ..helper.spider import jw_spider

@main.route('/')
def index():
    return render_template('hello.html')

@main.route('/wechat', methods = ['GET', 'POST'] )
def wechat_auth():
    wechat = init_wechat_sdk()
    if request.method == 'GET':
        token = 'tokenOf2017NJUHelper1s'
        query = request.args
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return echostr
        else:
            current_app.logger.warning(u"验证失败")
            return ''
    else:
        # ipconfig?
        query = request.args
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        return wechat_response(request.data, msg_signature=signature, timestamp=timestamp, nonce=nonce)

# @main.route('/<path>')
# def today(path):
#     base_dir = os.path.dirname(__file__)
#     resp = make_response(open(os.path.join(base_dir, path)).read())
#     # resp.headers["Content-type"]="application/json;charset=UTF-8"
#     return resp

# @main.route('/wechat/grade')
# def get_grade_start():
#     global openid
#     openid = request.args.get('openid')
#     if not openid:
#         return redirect(url_for('helper.get_grade',term=1))
#     else:
#         user = User.query.filter_by(wechat_id=openid).first()
#         if user is None or user.wechat_id is None:
#             return redirect(url_for('main.jw_login'))
#         else:
#             pwd = user.password
#             cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
#             pwd = cipher.decrypt(pwd)
#             data = {
#                 'userName': user.user_number,
#                 'password': pwd
#             }
#             user.spd = jw_spider()
#             user.spd.site = 0
#             user.spd.age = int(user.user_number[0:2])
#             login_res = user.spd.login(login_data=data)
#             if login_res == 'success':
#                 login_user(user)
#                 # return redirect(url_for('helper.get_grade_start', num=user.user_number))
#                 # if request.args.get('next'):
#                 #     next = url_for('main.index')+request.args.get('next')
#                 #     print(next)
#
#                 return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
#             else:
#                 user.spd.site = 1
#                 login_res = user.spd.login(login_data=data)
#                 if login_res == 'success':
#                     login_user(user)
#                     return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
#                 else:
#                     return redirect(url_for('main.jw_login', type=1))
#
# @main.route('wechat/jw_login')
# def jw_login(type=0):
#     form = wechat_JWLoginForm()
#     if type==1:
#         flash('您绑定的账号密码有误，请重新绑定！')
#     if form.validate_on_submit():
#         user = User.query.filter_by(wechat_id=openid).first()
#         site_choose = form.site.data
#         data = {
#             'userName': form.number.data,
#             'password': form.password.data
#         }
#         if user is None:
#             new_user = User()
#             new_user.wechat_id = openid
#             db.session.add(new_user)
#             db.session.commit()
#             user = User.query.filter_by(wechat_id=openid).first()
#
#         # user.create_spd()
#         if form.rem_wechat.data == True:
#             #加密账号密码并储存
#             user.user_number = form.number.data
#             cipher = AESCipher(current_app.config['PASSWORD_SECRET_KEY'])
#             pwd = cipher.encrypt(form.password.data)
#             user.password = pwd
#         user.spd=jw_spider()
#         user.spd.site = int(site_choose)
#         # user.spd.set_age(int(form.number.data[0:2]))
#         # user.test_id = 1
#         user.spd.age = int(form.number.data[0:2])
#         login_res = user.spd.login(login_data=data)
#         if login_res == 'success':
#             login_user(user)
#             # return redirect(url_for('helper.get_grade_start', num=user.user_number))
#             # if request.args.get('next'):
#             #     next = url_for('main.index')+request.args.get('next')
#             #     print(next)
#
#             return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
#         else:
#             flash(login_res)
#     return render_template('helper/login.html', form=form, message=current_app.config['REMEMBER_PASSWORD_MESSAGE'])