import json

import requests
from flask import Flask, render_template, redirect
from flask_restful import Api, abort

from data import db_session
from resourse import users_resource, post_resource
from data.user import User
from forms.login_form import LoginForm
from forms.reg_form import RegForm
from forms.message_form import MessForm
from forms.chat_form import ChatForm
from flask_login import login_user, LoginManager, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_project_secret_key_ppooiizzxxcc'
api = Api(app)
login_magager = LoginManager()
login_magager.init_app(app)


def main():
    api.add_resource(users_resource.UsersListResource, '/data/users')
    api.add_resource(users_resource.UsersResource, '/data/users/<int:user_id>')
    api.add_resource(post_resource.PostsListResource, '/data/posts/<user_data>')
    api.add_resource(post_resource.PostsResource, '/data/posts/<user_data>/<int:post_id>')
    db_session.global_init('db/users.db')
    app.run()


@login_magager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user


@app.route("/")
def redirect_login():
    return redirect('/login')


@app.route("/login", methods=["GET", "POST"])
def login():
    logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = sess.query(User).filter(User._login == form.login.data).first()
        if user and user.check_password(form.password.data):
            if form.remember_me.data:
                login_user(user, remember=form.remember_me.data)
            else:
                login_user(user, remember=False)
            return redirect("/info/users/" + str(current_user.id))

    return render_template("login.html", form=form)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    errors = ['Логин должен иметь только буквы и цифры (но не только одни цифры)',
              'Пароли не совпадают',
              'Этот логин уже занят',
              'Возраст должен быть целочисленным числом']
    form = RegForm()

    if form.validate_on_submit():

        sess = db_session.create_session()
        if sess.query(User).filter(User._login == form.login.data).first():
            return render_template("reg.html", form=form, error=errors[2])
        try:
            if form.password1.data == form.password2.data:
                my_data = {
                    'nick': form.nick.data,
                    'login': form.login.data,
                    'age': int(form.age.data),
                    'password': form.password1.data
                }
                requests.post(url='http://127.0.0.1:5000/data/users', data=my_data)
                user = sess.query(User).filter(User._login == form.login.data).first()
                if form.remember_me.data:
                    login_user(user, remember=form.remember_me.data)
                else:
                    login_user(user, remember=False)
                return redirect("/info/users/" + str(current_user.id))
            else:
                return render_template("reg.html", form=form, error=errors[1])
        except Exception as er:
            print(er)
            return render_template("reg.html", form=form, error=errors[0])

    return render_template("reg.html", form=form)


@app.route('/info/users/<int:user_id>')
def user_get(user_id):
    try:
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return redirect('/info/users/' + user.login)
    except:
        abort(404, message=f"User {user_id} not found")


@app.route('/info/users/<string:user_login>', methods=["GET", "POST"])
def user_login_get(user_login):
    errors = ['Вы заблокированы у этого пользователя']
    try:
        sess = db_session.create_session()
        user = sess.query(User).filter(User._login == user_login).first()
        if user.id == current_user.id:
            chats = user.get_chats()
            return render_template('home_page.html', title='User: @' + user.login, user_nick=current_user.nick,
                                   user_log=current_user.login, chats=chats)
        else:
            form = ChatForm()
            form.blocked.data = current_user.check_blocked(user.id)
            chats = current_user.get_chat(user.id)
            current_user.read_message(user.id)
            if form.validate_on_submit():
                my_data = {
                    'sender': current_user.login,
                    'recipient': user.login,
                    'header': form.header1.data,
                    'text': form.text.data
                }
                check = requests.post(url=f'http://127.0.0.1:5000/data/posts/{current_user.user_data()}',
                                      data=my_data).json()['POST']
                chats = current_user.get_chat(user.id)
                return redirect(f'{user.login}#begin')
            return render_template('chat.html', title='User: @' + user.login, user_nick=current_user.nick,
                                   user_log=current_user.login, chats=chats, form=form)

    except Exception as er:
        print(er)
        return redirect('/login')


@app.route('/info/users/write_message', methods=["GET", "POST"])
def write_message():
    errors = ['Вы не можете  отправить сообщение самому себе',
              'Чат заблокирован']
    form = MessForm()
    try:
        sender = current_user.login
        if form.validate_on_submit():
            if form.recipient.data == current_user.login:
                return render_template('message.html', title='Написать сообщение', user_log=current_user.login,
                                       user_nick=current_user.nick, form=form, error=errors[0])
            else:
                try:
                    my_data = {
                        'sender': sender,
                        'recipient': form.recipient.data,
                        'header': form.header1.data,
                        'text': form.text.data
                    }
                    check = requests.post(url=f'http://127.0.0.1:5000/data/posts/{current_user.user_data()}',
                                          data=my_data).json()['POST']
                    return redirect('/info/users/' + form.recipient.data)
                except:
                    return render_template('message.html', title='Написать сообщение', user_log=current_user.login,
                                           user_nick=current_user.nick, form=form, error=errors[1])
        return render_template('message.html', title='Написать сообщение', user_log=current_user.login,
                               user_nick=current_user.nick, form=form)
    except AttributeError:
        return redirect('/login')


if __name__ == '__main__':
    main()
