from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from wtforms import SubmitField, BooleanField, TextAreaField, StringField
from wtforms.validators import Length


class ChatForm(FlaskForm):
    blocked = BooleanField('Обновлять страницу?', default=True)
    header1 = StringField('Заголовок', validators=[Length(max=30)],
                          render_kw=dict(style='width: 200%; display: block;'))
    text = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=200)],
                         render_kw=dict(style='width: 65%; height: 100px; display: block; resize: none;'))
    submit = SubmitField('Отправить')
