#!/usr/bin/python3 
# -*- coding:utf-8 -*-
import datetime
import json
import random
import time
import uuid

import records
import redis
import requests
from flask import current_app

from app import scheduler, db
from app.common.functions import wechat_info_err
from datas.model.cron_infos import CronInfos
from datas.model.job_log import JobLog
from datas.utils.times import get_now_time, get_next_time

'''
定时操作
'''
def cron_do(cron_id):

    with scheduler.app.app_context():

        cif = CronInfos.query.get(cron_id)

        if not cif:
            jl = JobLog(cron_info_id=cron_id,content="定时任务不存在",create_time=get_now_time(),take_time=0)
            db.session.add(jl)
            db.session.commit()
        else:
            req_url = cif.req_url
            if not req_url:
                jl = JobLog(cron_info_id=cron_id, content="请求链接不存在", create_time=get_now_time(), take_time=0)
                db.session.add(jl)
                db.session.commit()
            else:
                if req_url.find('http') == -1:
                    jl = JobLog(cron_info_id=cron_id, content="请求链接有误，请检查一下", create_time=get_now_time(), take_time=0)
                    db.session.add(jl)
                    db.session.commit()
                else:
                    t = time.time()

                    req = requests.get(req_url,timeout=2*60,headers={'user-agent':'xmb_cron'})

                    ret = req.text

                    try:
                        ret = req.json()
                        errcode = ret.get('errcode')
                        if errcode:
                            if int(errcode) !=0:
                                wechat_info_err('定时任务【%s】发生错误' % cif.task_name,'返回信息:%s' % json.dumps(ret,ensure_ascii=False))
                    except:
                        pass

                    if type(ret) == dict:
                        ret = json.dumps(ret,ensure_ascii=False)

                    jl = JobLog(cron_info_id=cron_id, content=ret, create_time=get_now_time(),take_time=time.time() - t)
                    db.session.add(jl)
                    db.session.commit()

    return ""

def cron_check():
    with scheduler.app.app_context():
        def dbs():
            url = current_app.config.get('CRON_DB_URL')
            db = records.Database(url)
            db = db.get_connection()  # 新加
            return db

        job_db = dbs()
        job_arr = []
        jobs = job_db.query("select id from apscheduler_jobs").all()
        if jobs:
            for item in jobs:
                job_arr.append(item.id)

        cifs = CronInfos.query.all()

        if cifs:
            for item in cifs:
                if "cron_%s" % item.id not in job_arr:
                    item.status = -1
                    db.session.add(item)
                    db.session.commit()

    return

def cron_del_job_log():
    with scheduler.app.app_context():
        today = get_next_time(format='%Y-%m-%d',days=-14)
        sql = "delete from job_log where create_time < '%s 00:00'" % today
        db.session.execute(sql)
        db.session.commit()