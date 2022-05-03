from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from wtforms import SubmitField, PasswordField, EmailField, IntegerField, BooleanField
from wtforms.validators import Length


class RegForm(FlaskForm):
    def nick_check(self, field):
        if not field.data:
            field.data = self.login.data

    login = EmailField('Логин', validators=[DataRequired(), Length(max=20)])
    nick = EmailField('Имя', validators=[Length(max=30), nick_check])
    password1 = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    age = IntegerField('Возраст', default=0)
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регестрация')
