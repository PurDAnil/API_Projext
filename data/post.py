from datetime import datetime
import sqlalchemy
import base64
import json

from data.user import User
from .db_session import SqlAlchemyBase, create_session

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Post(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    _sender = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    _recipient = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    _header = sqlalchemy.Column(sqlalchemy.String, default='Message')
    _text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    modified_date = sqlalchemy.Column(sqlalchemy.String, default=datetime.now().strftime('%H:%M %d.%B.%Y'))

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, open_text):
        if not open_text:
            open_text = 'Message'
        self._header = base64.b64encode(bytes(open_text, encoding='UTF-8'))

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, open_text):
        self._text = base64.b64encode(bytes(open_text, encoding='UTF-8'))

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, open_text):
        sess = create_session()
        user = sess.query(User).filter(User._login == open_text).first()
        sess.commit()
        self._sender = user.id

    @property
    def recipient(self):
        return self._recipient

    @recipient.setter
    def recipient(self, open_text):
        sess = create_session()
        id_k = sess.query(Post).all()
        if id_k:
            self.id = id_k[-1].id + 1
        else:
            self.id = 1
        user = sess.query(User).filter(User._login == open_text).first()
        user1 = sess.query(User).filter(User.id == self._sender).first()
        if (not user.blocked or str(self._sender) not in user.blocked.split(';')) or\
                (not user1.blocked or str(user.id) not in user1.blocked.split(';')):
            if not user.messages:
                user.messages = json.dumps({self._sender: [self.id]})
            else:
                mess = json.loads(user.messages)
                if str(self._sender) in mess.keys():
                    mess[str(self._sender)].append(self.id)
                else:
                    mess[str(self._sender)] = []
                    mess[str(self._sender)].append(self.id)
                user.messages = json.dumps(mess)

            if not user1.messages:
                user1.messages = json.dumps({user.id: [self.id]})
            else:
                mess = json.loads(user1.messages)
                if str(user.id) in mess.keys():
                    mess[str(user.id)].append(self.id)
                else:
                    mess[str(user.id)] = []
                    mess[str(user.id)].append(self.id)
                user1.messages = json.dumps(mess)
            if not user.not_read:
                user.not_read = self._sender
            elif str(self._sender) not in user.not_read:
                user.not_read += ';' + str(self._sender)
            if not user1.not_read:
                user1.not_read = user.id
            elif str(user.id) not in user1.not_read:
                user1.not_read += ';' + str(user.id)
            sess.commit()
            self._recipient = user.id