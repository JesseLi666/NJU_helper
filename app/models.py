import base64

from Crypto import Random
from Crypto.Cipher import AES
from flask_login import UserMixin

from .spider import jw_spider
from . import db, login_manager


class User(UserMixin, db.Model):

    def create_spd(self):
        # self.spd = None
        self.spd = jw_spider()

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_number = db.Column(db.String(64), index=True)
    # user_number = db.Column(db.String(64), unique=True, index=True)
    wechat_id = db.Column(db.String(64), unique=True, index=True)
    # password_hash = db.Column(db.String(128))
    password = db.Column(db.String(64))
    name = db.Column(db.String(64))
    # 需要补全，密码要加密
    spd = db.Column(db.PickleType)
    remember_me = db.Column(db.BOOLEAN)
    # spd = jw_spider()

    # test_id = db.Column(db.Integer)

    grades = db.relationship('Grade', backref='stu', lazy='dynamic')
    courses = db.relationship('Course', backref='stu', lazy='dynamic')

    def delete_password(self):
        self.user_number = None
        self.password = None
        self.remember_me = False

    def get_courses_from_database(self):
        ts = self.courses.all()
        res = []
        for t in ts:
            temp = []
            if t.name:
                temp.append(t.name)
                temp.append(t.teacher)
                temp.append(t.place_time)
                temp.append(t.course_num)
                temp.append(t.type)
                temp.append(t.campus)
                res.append(temp)
        return res

    def save_courses_into_database(self, courses, stu):
        ts = self.courses.all()
        for t in ts:
            if t.type != '新增':
                db.session.delete(t)

        for c in courses:
            tt = Course(stu=stu, name=c[0], teacher=c[1], place_time=c[2],
                        course_num=c[3], type=c[4], campus=c[5])
            db.session.add(tt)
        db.session.commit()

    # 暂时用不到
    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute')
    #
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     return check_password_hash(self.password_hash, password)
    ###


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    course_num = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    name_eng = db.Column(db.String(64))
    type = db.Column(db.String(64))
    weight = db.Column(db.Integer)
    score = db.Column(db.Integer)
    remark = db.Column(db.String(64))
    stu_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_num = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    campus = db.Column(db.String(64))
    teacher = db.Column(db.String(64))
    type = db.Column(db.String(64))
    place_time = db.Column(db.Text)

    stu_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class AESCipher():
    """
    加密解密方法
    http://stackoverflow.com/questions/12524994
    """

    def __init__(self, key):
        self.BS = 16
        self.pad = lambda s: s + \
            (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        self.key = key

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))
