from flask_mail import Message
from .. import mail
from flask import current_app, render_template
from ..decorators import async


# @async
# def send_async_email(app, msg):
#     with app.app_context():
#         rsp = mail.send(msg)


def send_email(msg):
    from manage import celery

    @celery.task
    def send_async_email(msg):
        # 在make_celery中已经配置过flask上下文了，所以不需要app.app_context
        rsp = mail.send(msg)
        current_app.logger.info("send email: " + str(rsp))

    send_async_email(msg)


def send_email_by_suggestion(template, **kwargs):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' New suggestion',
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[current_app.config['SEND_MAIL_TO']])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    send_email(msg)


def send_email_by_error(error_msg):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' An error occurred',
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[current_app.config['SEND_MAIL_TO']])
    msg.body = error_msg

    send_email(msg)
