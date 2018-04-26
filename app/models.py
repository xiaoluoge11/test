#!/usr/bin/env python
# coding:utf-8
import datetime, time
from sqlalchemy.sql.sqltypes import TIMESTAMP, Date 
from ext import db


class User(db.Model):
    __tablename__    = 'user'
    id               = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name             = db.Column(db.String(50), nullable=False,comment="名称")
    readname         = db.Column(db.String(50), nullable=False,comment="中文名")
    password         = db.Column(db.String(50),nullable=False,comment="密码")
    email            = db.Column(db.String(50), nullable=False,comment="邮件")
    phone            = db.Column(db.String(50),comment="电话")
    status           = db.Column(db.Integer, default=0,comment="状态，0表示正常，1表示禁用")
    r_id             = db.Column(db.Integer,default=1,comment="1有权限查看所有")
