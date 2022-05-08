from datetime import datetime
import sqlalchemy
import requests
import base64
import json

from . import db_session
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    _login = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    nick = sqlalchemy.Column(sqlalchemy.String, default=_login)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    _password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    messages = sqlalchemy.Column(sqlalchemy.String, default=None)
    not_read = sqlalchemy.Column(sqlalchemy.String, default=None)
    blocked = sqlalchemy.Column(sqlalchemy.String, default=None)
    last = sqlalchemy.Column(sqlalchemy.String, default='')
    reg_date = sqlalchemy.Column(sqlalchemy.String, default=datetime.now().strftime('%d.%B.%Y'))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, open_text):
        if len(open_text) >= 8:
            self.set_password(open_text)

    def set_password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, open_text):
        if len(open_text) <= 20 and (open_text.isalnum() or open_text.isalpha()) and not open_text.isnumeric():
            self._login = open_text

    def check_blocked(self, user_id):
        if self.blocked and str(user_id) in self.blocked.split(';'):
            return True
        return False

    def add_blocked_user(self, user_id):
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == self.id).first()
        if not user.blocked or str(user_id) not in user.blocked.split(';'):
            if user.blocked:
                user.blocked += ';' + str(user_id)
            else:
                user.blocked = str(user_id)
        sess.commit()

    def del_blocked_user(self, user_id):
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == self.id).first()
        if user.blocked and str(user_id) in user.blocked.split(';'):
            blocked = []
            for i in user.blocked.split(';'):
                if i != str(user_id):
                    blocked.append(i)
            user.blocked = ';'.join(blocked)
        sess.commit()

    def user_data(self):
        return f'{self.id}@{self.password}'

    def read_message(self, user_id: int):
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == self.id).first()
        user_id = str(user_id)
        if user_id in user.not_read.split(';'):
            not_read = user.not_read.split(';')
            not_read1 = []
            for i in not_read:
                if i != user_id:
                    not_read1.append(i)
            user.not_read = ';'.join(not_read1)
        sess.commit()

    def get_chats(self):
        try:
            chats = [int(i) for i in self.last.split(';')]
            chats.reverse()
            sess = db_session.create_session()
            for i, el in enumerate(chats):
                user = sess.query(User).filter(User.id == el).first()
                if self.not_read and str(el) in self.not_read.split(';'):
                    color = '#78aeff'
                elif self.blocked and str(el) in self.blocked.split(';'):
                    color = '#ff7878'
                else:
                    color = '#b5b5b5'
                req = requests.get(url=f'http://127.0.0.1:5000/data/posts/{self.user_data()}/'
                                       f'{json.loads(self.messages)[str(el)][-1]}').json()['GET'][0]['post']
                text = base64.b64decode(req['text']).decode('UTF-8')[:30]
                if len(base64.b64decode(req['text']).decode('UTF-8')) > 30:
                    text += '...'
                header = base64.b64decode(req['header']).decode('UTF-8')[:15]
                if len(base64.b64decode(req['header']).decode('UTF-8')) > 15:
                    text += '...'
                chats[i] = [user.nick, user.login, color, header, text]
            sess.close()
            return chats
        except:
            return [['У вас нет сообщений', self._login, '#78aeff', '', '']]

    def get_chat(self, user_id):
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == user_id).first()
        try:
            if self.not_read and str(user_id) in self.not_read.split(';'):
                color = '#78aeff'
            elif self.blocked and str(user_id) in self.blocked.split(';'):
                color = '#ff7878'
            else:
                color = '#b5b5b5'
            messages = json.loads(self.messages)[str(user_id)]
            mess = []
            for i in messages:
                req = requests.get(
                    url=f'http://127.0.0.1:5000/data/posts/{self.user_data()}/{i}').json()['GET'][0]['post']
                if req['sender'] == self.id:
                    sen = True
                else:
                    sen = False
                mes = [base64.b64decode(req['header']).decode('UTF-8'), base64.b64decode(req['text']).decode('UTF-8'),
                       req['modified_date'], sen]
                mess.append(mes)
            chat = [user.nick, user.login, color, mess]
        except Exception as er:
            print(er)
            chat = [user.nick, user.login, '#78aeff', []]
        sess.close()
        return chat

    def __repr__(self):
        return f"@{self.login} {self.nick} {self.age}"
