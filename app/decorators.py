from functools import wraps
from flask import current_app, abort, redirect
import urllib.request
from .helper.spider import jws

def jw_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        test_url = current_app.config['JW_BASE_URL'][0]
        try:
            test_req = jws.get(test_url, allow_redirects=False, timeout = 1).status_code
        except:
            test_req = 302
        if test_req != 200:
            test_url = current_app.config['JW_BASE_URL'][1]
            try:
                test_req = jws.get(test_url, allow_redirects=False, timeout=1).status_code
            except:
                test_req = 302
            if test_req != 200:
                abort(403)
        return f(*args, **kwargs)
    return decorated_function



