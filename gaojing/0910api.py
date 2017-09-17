#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
from datetime import datetime
import subprocess
from flask import Flask, abort, request, jsonify, g, url_for, render_template, redirect,flash, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer                          as Serializer, BadSignature, SignatureExpired)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://soul:soul@127.0.0.1:3306/gaojingdb'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
#bootstrap
from flask.ext.bootstrap import Bootstrap
bootstrap = Bootstrap(app)

#forms
class LoginForm(FlaskForm):
    email = StringField(u'邮件', validators=[Required(), Length(1, 64),Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField('记住账号')
    submit = SubmitField(u'登陆')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(512))
    tokenkey = db.Column(db.String(512))
    phone = db.Column(db.String(16))
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=6000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/', methods=['GET','POST'])
def index():

    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('user',username=user.username))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    phone = request.json.get('phone')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username,phone=phone)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username,'phone': user.phone}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(6000)
    User.query.filter_by(username='%s' % g.user.username).update({'tokenkey': '%s' % token }) 
    #注意这里的用户名和token数值一定要以参数形式传进去 
    #return jsonify({'token': token.decode('ascii'), 'duration': 600})  #其实要不要decode('ascii')都是可以的
    return jsonify({'token': token, 'duration': 6000})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    #phone = g.user.phone
    if g.user.tokenkey is not None: #token不为空时执行拨打规则
            subprocess.call(['/usr/sbin/asterisk -rx "originate Local/%s@OUTBOUND extension"' % g.user.phone],shell=True)
    	    return jsonify({'data': 'Hello, %s!' % g.user.username,'calling': '%s' % g.user.phone })
    #return jsonify({'token': token.decode('ascii'), 'duration': 600})

if __name__ == '__main__':
     db.create_all()
     app.run(host='0.0.0.0',debug=True)
