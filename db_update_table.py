#!/usr/bin/env python
# coding:utf-8

import os,util 
from app import app,db 
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app.models import User  
from sqlalchemy.sql.sqltypes import TIMESTAMP, TEXT


work_dir = os.path.dirname(os.path.realpath(__file__))

service_conf = os.path.join(work_dir, 'conf/service.conf')
config =util.get_config(service_conf, 'common')

app.config.from_object('config')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)
@manager.shell
def make_shell_context():
        return dict(app=app, db=db, Idc=Idc,User=User, Server=Server)



if __name__ == "__main__":
    manager.run()
