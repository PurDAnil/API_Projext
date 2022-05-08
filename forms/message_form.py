from data.user import User
from data.db_session import create_session
from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import Length, ValidationError


class MessForm(FlaskForm):
    def rec_check(self, field):
        if not field.data.isalnum() and not field.data.isalpha():
            raise ValidationError('Неверный формат тега')
        sess = create_session()
        if not sess.query(User).filter(User._login == field.data).first():
            raise ValidationError('Пользователь с такм тегом не найден')

    recipient = StringField('Тег получателя', validators=[DataRequired(), Length(max=30), rec_check])
    header1 = StringField('Заголовок', validators=[Length(max=15)])
    text = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=1000)],
                         render_kw=dict(style='height: 100px; display: block;'))
    submit = SubmitField('Отправить')
