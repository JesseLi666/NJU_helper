from flask import render_template, redirect, url_for, request, abort, flash,\
    current_app, make_response
from flask_login import login_required, current_user, login_user, logout_user
from . import helper
from .. import db
from ..models import User, Grade
from .forms import JWLoginForm
from ..decorators import jw_login_required
from .spider import jw_spider


@helper.route('/jw_login', methods=['GET', 'POST'])
def jw_login():
    form = JWLoginForm()
    if form.validate_on_submit():
        site_choose = form.site.data
        ###
        data = {
            'userName': form.number.data,
            'password': form.password.data
        }
        user = User.query.filter_by(user_number=form.number.data).first()
        if user is None:
            new_user = User()
            new_user.user_number=form.number.data
            db.session.add(new_user)
            db.session.commit()

        user = User.query.filter_by(user_number=form.number.data).first()
        # user.create_spd()
        user.spd=jw_spider()
        user.spd.site = int(site_choose)
        # user.spd.set_age(int(form.number.data[0:2]))
        # user.test_id = 1
        user.spd.age = int(form.number.data[0:2])
        login_res = user.spd.login(login_data=data)
        if login_res == 'success':
            login_user(user)
            # return redirect(url_for('helper.get_grade_start', num=user.user_number))
            return redirect(request.args.get('next') or url_for('helper.get_grade_start', num=user.user_number))
        else:
            flash(login_res)
    return render_template('login.html',form=form)

@helper.route('/grade')
@jw_login_required
def get_grade_start_all():
    return redirect(url_for('helper.get_grade_start', num=current_user.user_number))

@helper.route('/grades/<num>', methods=['GET', 'POST'])
# @login_required
@jw_login_required
def get_grade_start(num):
    return redirect(url_for('helper.get_grade', num=num, term=1))

@helper.route('/grades/<num>/<int:term>', methods=['GET', 'POST'])
# @login_required
@jw_login_required
def get_grade(num, term):
    if num != current_user.user_number:
        return redirect(url_for('helper.get_grade_start', num=current_user.user_number))
    try:
        grade_res = current_user.spd.get_grade(age=current_user.spd.age, term=term)
    except:
        grade_res = [ [],[],[],[] ]
    cnt = len(grade_res[0])
    total_term = (16 - current_user.spd.age) * 2 + 1
    return render_template('helper/grade.html', grades = grade_res, terms=total_term, term_now = term, cnt = cnt, base_url = current_user.spd.base_url)

@helper.route('/jw_logout')
# @login_required
@jw_login_required
def jw_logout():
    current_user.spd.logout()
    logout_user()
    return redirect(url_for('helper.jw_login'))
