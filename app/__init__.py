from flask import Flask, logging
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
# from config import config
import config
from flask_bootstrap import Bootstrap
from redis import Redis
import jinja2

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
redis = Redis()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)
    # app.config.from_pyfile('../config.py')

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    #
    # my_loader = jinja2.ChoiceLoader([
    #     app.jinja_loader,
    #     jinja2.FileSystemLoader('/path/to/templates'),
    # ])
    # app.jinja_loader = my_loader

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .helper import helper as helper_blueprint
    app.register_blueprint(helper_blueprint)

    return app
