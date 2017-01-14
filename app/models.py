from datetime import  datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db\
    # , login_manager

class User(UserMixin, db.Model):
    __table__name = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_number = db.Column(db.String(64), unique=True, index=True)
    wechat_id = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    grades = db.relationship('Grade', backref='stu', lazy='dynamic')
    ###需要补全，密码要加密

    def __init__(self, **kwargs):
        pass

    #暂时用不到
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    ###




class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    course_num = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    name_eng = db.Column(db.String(64))
    type = db.Column(db.String(64))
    weight = db.Column(db.Integer)
    score = db.Column(db.Integer)
    remark = db.Column(db.String(64))
    stu_id = db.Column(db.Integer, db.ForeignKey('users.id'))

