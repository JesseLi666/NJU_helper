from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_bootstrap import Bootstrap
import jinja2

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

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
