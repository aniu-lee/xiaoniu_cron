#!/usr/bin/env python
#coding:utf-8
import os

import requests
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.common.functions import wechat_info_err
from configs import configs
from datas.model.cron_infos import CronInfos

from datas.model.job_log import JobLog

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)

migrate = Migrate(app, db)

def make_shell_context():
    return dict(
        app=app,
        JobLog=JobLog,
        CronInfos=CronInfos
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    # cron_check()
    # wechat_info_err('1','1')
    # req = requests.post("http://127.0.0.1:5000/api/cron",data={'task_name':'demo','run_date':'','req_url':'11','second':'*/20'})
    # print(req.text)
    # cron_del_job_log()
    wechat_info_err('BUG来了')
    pass


if __name__ == '__main__':
    #gunicorn -b 127.0.0.1:5000 -w 1 -k gevent manage:app
    manager.run()
