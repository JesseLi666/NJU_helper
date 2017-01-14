from flask import render_template, redirect, url_for, request, abort, flash,\
    current_app, make_response
# from flask_login import login_required, current_user
from . import helper
from .. import db
from ..models import User, Grade
from .forms import JWLoginForm
from ..decorators import jw_login_required
from .spider import jw_spider

spd = jw_spider(0)

@helper.route('/jw_login', methods=['GET', 'POST'])
def jw_login(spd=spd):
    form = JWLoginForm()
    if form.validate_on_submit():
        site_choose = form.site.data
        ###
        spd.site=int(site_choose)
        # spd = jw_spider(int(site_choose))
        data = {
            'userName': form.number.data,
            'password': form.password.data
        }
        spd.age = int(form.number.data[0:2])
        login_res = spd.login(login_data=data)
        if login_res == 'success':
            return redirect(request.args.get('next') or url_for('helper.get_grade_start'))
        else:
            flash(login_res)
    return render_template('login.html',form=form)

@helper.route('/grade', methods=['GET', 'POST'])
@jw_login_required
def get_grade_start(spd=spd):
    return redirect(url_for('helper.get_grade', term=1))

@helper.route('/grades/<int:term>', methods=['GET', 'POST'])
@jw_login_required
def get_grade(term, spd=spd):
    #spd可以去掉吗
    grade_res = spd.get_grade(age=spd.age, term=term)
    cnt = len(grade_res[0])
    total_term = (16 - spd.age) * 2 + 1
    return render_template('helper/grade.html', grades = grade_res, terms=total_term, term_now = term, cnt = cnt, base_url = spd.base_url)

@helper.route('/jw_logout')
@jw_login_required
def jw_logout(spd=spd):
    spd.logout()
    return redirect(url_for('helper.jw_login'))



