from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from wtforms import SubmitField, BooleanField, PasswordField, EmailField


class LoginForm(FlaskForm):
    login = EmailField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
