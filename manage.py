#!/usr/bin/env python
#coding:utf-8
import os

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.common.functions import dd_push
from datas.model.cron_infos import CronInfos

from datas.model.job_log import JobLog
from datas.model.job_log_items import JobLogItems

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)

migrate = Migrate(app, db)

def make_shell_context():
    return dict(
        app=app,
        JobLog=JobLog,
        CronInfos=CronInfos,
        JobLogItems=JobLogItems
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    pass

if __name__ == '__main__':
    #gunicorn -b 127.0.0.1:5000 -w 1 -k gevent manage:app
    manager.run()
