from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, TextAreaField
from wtforms.validators import Required, Length, EqualTo, Regexp
from wtforms import ValidationError

class JWLoginForm(FlaskForm):
    number = StringField('学号', validators=[Required(), Length(9,9)])
    password = PasswordField('密码', validators=[Required()])
    site = RadioField('站点', choices=[('0', '站点1'), ('1', '站点2')], default=0)
    submit = SubmitField('登陆')

class wechat_JWLoginForm(FlaskForm):
    number = StringField('学号', validators=[Required(), Length(9,9)])
    password = PasswordField('密码', validators=[Required()])
    site = RadioField('站点', choices=[('0','站点1'), ('1', '站点2')], default=0)
    rem_wechat = BooleanField('将教务系统账号与我的微信绑定')
    submit = SubmitField('登陆')

class suggestForm(FlaskForm):
    suggestion = TextAreaField('您的问题或建议', validators=[Required()])
    submit = SubmitField('提交')



