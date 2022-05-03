import requests
from flask import Flask, render_template, redirect
from flask_restful import Api, abort

from data import db_session
from resourse import users_resource
from data.user import User
from forms.login_form import LoginForm
from forms.reg_form import RegForm
from flask_login import login_user, LoginManager, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_project_secret_key_ppooiizzxxcc'
api = Api(app)
login_magager = LoginManager()
login_magager.init_app(app)


def main():
    api.add_resource(users_resource.UsersListResource, '/data/users')
    api.add_resource(users_resource.UsersResource, '/data/users/<int:user_id>')
    db_session.global_init('db/users.db')
    app.run()


@login_magager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user


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
    errors = ['Логин должен иметь только буквы и цифры (но не только одни цыфры)',
              'Пароли не совпадают',
              'Этот логин уже занят',
              'Возраст должен быть целочисленным числом']

    logout_user()
    form = RegForm()

    if form.validate_on_submit():

        print(form.age.data)

        sess = db_session.create_session()
        if sess.query(User).filter(User._login == form.login.data).first():
            return render_template("reg.html", form=form, error=errors[3])
        try:
            if form.password1.data == form.password2.data:
                my_data = {
                    'nick': form.nick.data,
                    'login': form.login.data,
                    'age': int(form.age.data),
                    'password': form.password1.data
                }
                print(requests.post(url='http://127.0.0.1:5000/data/users', data=my_data).json())
                user = sess.query(User).filter(User._login == form.login.data).first()
                if form.remember_me.data:
                    login_user(user, remember=form.remember_me.data)
                else:
                    login_user(user, remember=False)
                return redirect("/info/users/" + str(current_user.id))
            else:
                return render_template("reg.html", form=form, error=errors[1])
        except:
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


@app.route('/info/users/<user_login>')
def user_login_get(user_login):
    user_login = str(user_login)
    try:
        sess = db_session.create_session()
        user = sess.query(User).filter(User._login == user_login).first()
        return render_template('base.html', title='User: @' + user.login, user_nick=current_user.nick,
                               user_log=current_user.login)
    except:
        return redirect('/login')


if __name__ == '__main__':
    main()
