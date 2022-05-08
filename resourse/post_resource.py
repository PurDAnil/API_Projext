from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.post import Post
from data.user import User

parser = reqparse.RequestParser()

parser.add_argument('id', type=int)
parser.add_argument('recipient', required=True)
parser.add_argument('header')
parser.add_argument('text', required=True)


def not_found(funk, post_id):
    session = db_session.create_session()
    users = session.query(Post).get(post_id)
    if not users:
        abort(404, message=f"Post.{funk}: Post {post_id} not found")


class PostsResource(Resource):
    def get(self, user_data, post_id):

        user_data = user_data.split('@')
        not_found('GET', post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        if post.sender == int(user_data[0]) or post.recipient == int(user_data[0]):
            user = session.query(User).filter(User.id == user_data[0]).first()
            if post.sender != post.recipient and user.password == user_data[1]:
                return jsonify(
                    {'GET': [{'post': post.to_dict(only=('id', 'header', 'text', 'modified_date'))}]})
            else:
                not_found('GET', post_id)
        else:
            not_found('GET', post_id)


class PostsListResource(Resource):
    def post(self, user_data):
        user_data = user_data.split('@')
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_data[0]).first()
        post = None
        if user.password == user_data[1]:
            post = Post(id=args['id'],
                        sender=user.login,
                        recipient=args['recipient'],
                        header=args['header'],
                        text=args['text']
                        )
        try:
            session.add(post)
            session.commit()
            return jsonify({'POST': [{'user': post.to_dict(only=('id', 'sender', 'recipient', 'header'))},
                                     {'success': 'OK'}]})
        except Exception:
            abort(404, message=f"Post.POST: Incorrect data")
