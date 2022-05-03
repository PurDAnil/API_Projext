from datetime import datetime
import sqlalchemy
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
    _password = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.String, default=datetime.now().strftime('%d.%B.%Y'))

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

    def __repr__(self):
        return f"@{self.login} {self.nick} {self.age}"
