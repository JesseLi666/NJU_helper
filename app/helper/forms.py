from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import Required, Length, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User

class JWLoginForm(Form):
    number = StringField('学号', validators=[Required(), Length(9,9)])
    password = PasswordField('密码', validators=[Required()])
    site = RadioField('站点', choices=[('0','站点1'), ('1', '站点2')])
    submit = SubmitField('登陆')





