from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.post import Post

parser = reqparse.RequestParser()

parser.add_argument('id', type=int)
parser.add_argument('sender', required=True)
parser.add_argument('recipient', required=True)
parser.add_argument('header')
parser.add_argument('text', required=True)


def not_found(funk, post_id):
    session = db_session.create_session()
    users = session.query(Post).get(post_id)
    if not users:
        abort(404, message=f"User.{funk}: User {post_id} not found")


class UsersResource(Resource):
    def get(self, post_id):

        not_found('GET', post_id)
        session = db_session.create_session()
        user = session.query(Post).get(post_id)
        return jsonify({'GET': [{'user': user.to_dict(only=('nick', 'login', 'age'))}]})


class UsersListResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(id=args['id'],
                    sender=args['sender'],
                    recipient=args['recipient'],
                    header=args['header'],
                    text=args['text']
                    )
        try:
            session.add(post)
            session.commit()
            return jsonify({'POST': [{'user': post.to_dict(only=('id', 'sender', 'recipient', 'header'))},
                                     {'success': 'OK'}]})
        except:
            abort(404, message=f"Post.POST: Incorrect data")
