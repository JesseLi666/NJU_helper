from functools import wraps
from flask import current_app, abort, redirect, url_for
import urllib.request
# from .helper.spider import jws
from flask_login import current_user

def jw_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('helper.jw_login'))
        test_url = current_app.config['JW_BASE_URL'][0] + 'student/studentinfo/index.do'
        try:
            test_req = current_user.spd.jws.get(test_url, allow_redirects=False, timeout = 1).status_code
        except:
            test_req = 302
        if test_req != 200:
            test_url = current_app.config['JW_BASE_URL'][1] + 'student/studentinfo/index.do'
            try:
                test_req = current_user.spd.jws.get(test_url, allow_redirects=False, timeout=1).status_code
            except:
                test_req = 302
            if test_req != 200:
                return redirect(url_for('helper.jw_login'))
                pass

        return f(*args, **kwargs)
    return decorated_function



