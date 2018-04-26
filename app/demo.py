#coding:utf-8
from __future__ import unicode_literals                                                                                                                      
from flask import Flask, render_template,session,redirect,request,url_for
from  . import app,db  
import requests,json
import util
from util import *
import sys,json
from models import User
reload(sys)
sys.setdefaultencoding('utf8')

headers = {'content-type': 'application/json'}
        

#适用于比较简单多功能，直接/htmlname 就能访问到,eg:deshboard
@app.route('/<htmlname>')   
def single(htmlname):
    if htmlname.endswith('html'):
        return render_template(htmlname)
    else:
        return render_template(htmlname+'.html')
