from . import helper
from flask import render_template


@helper.app_errorhandler(403)
def forbiddens(e):
    return render_template('403.html'),403


@helper.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


@helper.app_errorhandler(500)
def internal_server_error(e):
    return  render_template('500.html'),500