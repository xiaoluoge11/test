#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
from datetime import datetime
import subprocess
from flask import Flask, abort, request, jsonify, g, session, url_for, render_template, redirect, flash, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, UserMixin, AnonymousUserMixin
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#forms
class LoginForm(FlaskForm):
    email = StringField(u'邮件', validators=[Required(), Length(1, 64),Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField('记住账号')
    submit = SubmitField(u'登陆')

class RegistrationForm(FlaskForm):
    email = StringField(u'邮件地址', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母,下划线,数字')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo('password2', message='确认密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'确 定')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮件已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该用户名已被注册')

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(512))
    token = db.Column(db.String(512))
    phone = db.Column(db.String(16), unique=True, index=True)
    telphone = db.Column(db.String(16), unique=True, index=True)
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    number = db.Column(db.String(16))
    total = db.Column(db.String(16))
    status = db.Column(db.String(16))
    clientip = db.Column(db.String(64))

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
@app.route('/index', methods=['GET','POST'])
def index():

    return render_template('index.html')

@app.route('/jieru', methods=['GET','POST'])
def jieru():

    return render_template('jieru.html')

#@app.route('/api/users', methods=['POST'])
#def new_user():
#    username = request.json.get('username')
#    password = request.json.get('password')
#    if username is None or password is None:
#        abort(400)    # missing arguments
#    if User.query.filter_by(username=username).first() is not None:
#        abort(400)    # existing user
#    user = User(username=username)
#    user.hash_password(password)
#    db.session.add(user)
#    db.session.commit()
#    return (jsonify({'username': user.username}), 201,
#            {'Location': url_for('get_user', id=user.id, _external=True)})




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data)
        #token = user.generate_confirmation_token()
        user.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #token = user.generate_confirmation_token()
        #send_email(user.email, 'Confirm Your Account',
        #           'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            username=user.username
            session['remember_me'] = form.remember_me.data
            session['username'] = username
            #login_user(user, form.remember_me.data)
            #return redirect(url_for('user.html',username=user.username))
            return redirect(url_for('user',username=user.username))  #这里一定要加url_for
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #page = request.args.get('page', 1, type=int)
    #pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
     #   page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
      #  error_out=False)
    #posts = pagination.items
    return render_template('/page/user.html', user=user)

@app.route('/page/<template>')
def render(template):
    #if 'username' in session:
       # username=session['username']
        #user = User.query.filter_by(username=username).first_or_404()
        return render_template('page/'+template+'.html',user=user)
    #else:
     #   return redirect('/login')



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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    #if 'remember_me' in session:
       # remember_me = session['remember_me']
        #session.pop('remember_me', None)
        #return redirect(url_for('/login'))
    flash('You have been logged out.')
    return redirect(url_for('/login'))

if __name__ == '__main__':
     db.create_all()
     app.run(host='0.0.0.0',debug=True)
