from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField, ValidationError
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, InputRequired
from app.models import UserModel


# Form:主要就是用来验证前端提交的数据是否符合要求
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 20, message="")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 20, message="")])
    password_confirm = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message="两次输入密码不一致")])
    submit = SubmitField('Register')

    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise ValidationError(message="该邮箱已经被注册!")

    def validate_username(self, username):
        user = UserModel.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 20)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    title = StringField('title', validators=[Length(min=3, max=100)])
    content = StringField('content', validators=[Length(min=3)])
    submit = SubmitField('POST')


class CommentForm(FlaskForm):
    content = StringField('content', validators=[Length(min=3, message="内容格式错误!")])
    post_id = IntegerField('post_id', validators=[InputRequired(message="必须要传入问题id!")])
    submit = SubmitField('POST')
