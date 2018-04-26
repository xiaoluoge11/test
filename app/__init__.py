from flask import Flask   
from sqlalchemy.sql.sqltypes import TIMESTAMP, TEXT
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from ext import db
from models import User

app = Flask(__name__)    
app.config.from_object('config')
db.init_app(app) 


import demo
