from flask import Flask, logging
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_bootstrap import Bootstrap
from redis import Redis
import jinja2
from celery import Celery

import config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
redis = Redis()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])

    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

<<<<<<< Updated upstream
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1, encoding='utf8')
=======

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=10)
>>>>>>> Stashed changes
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .helper import helper as helper_blueprint
    app.register_blueprint(helper_blueprint)

    return app


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
