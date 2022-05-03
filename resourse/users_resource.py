import sqlite3

from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.user import User

parser = reqparse.RequestParser()
parser.add_argument('id', type=int)
parser.add_argument('nick', required=True)
parser.add_argument('age', type=int)
parser.add_argument('login', required=True)
parser.add_argument('password', required=True)


def not_found(funk, user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User.{funk}: User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        not_found('GET', user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'GET': [{'user': user.to_dict(only=('nick', 'login', 'age'))}]})

    def delete(self, user_id):
        not_found('DELETE', user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'DELETE': [{'user': user.to_dict(only=('id', 'nick', 'login', 'age'))},
                                   {'success': 'OK'}]})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'nick', 'login', 'age')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(id=args['id'],
                    nick=args['nick'],
                    age=args['age'],
                    password=args['password'],
                    login=args['login']
                    )
        try:
            session.add(user)
            session.commit()
            return jsonify({'POST': [{'user': user.to_dict(only=('id', 'nick', 'login', 'age'))},
                                     {'success': 'OK'}]})
        except:
            abort(404, message=f"User.POST: Incorrect data")
