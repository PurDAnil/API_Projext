from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from wtforms import SubmitField, PasswordField, EmailField, StringField, BooleanField
from wtforms.validators import Length, ValidationError


class RegForm(FlaskForm):
    def nick_check(self, field):
        if not field.data:
            field.data = self.login.data

    def age_check(self, field):
        if not field.data:
            field.data = '0'
        elif not field.data.isnumeric():
            raise ValidationError('Возраст должен быть числом')

    login = EmailField('Логин', validators=[DataRequired(), Length(max=20)])
    nick = EmailField('Имя', validators=[Length(max=30), nick_check])
    password1 = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    age = StringField('Возраст', default=0, validators=[age_check])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регестрация')
