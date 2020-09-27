#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from flask import request

from app import scheduler, db
from app.decorated import api_deal_return, api_err_return
from datas.model.cron_infos import CronInfos
from . import api
from ..crons import cron_do


'''
添加（更新）定时
task_name 任务名称唯一
task_keyword 备注
run_date 执行时间
day
day_of_week
hour
minute
second
req_url
'''
@api.route('/cron/add',methods=['GET','POST'])
@api.route('/cron',methods=['GET','POST'])
@api_deal_return
def crons():

    datas = request.values.to_dict()

    task_name = datas.get('task_name')

    task_keyword = datas.get('task_keyword') or ''

    if not task_name:
        return api_err_return(msg='任务名称不能为空')

    cif = CronInfos.query.filter(CronInfos.task_name == task_name).first()

    run_date = datas.get('run_date') or ''

    day = datas.get('day') or ''

    if day:
        if day.isdigit() and int(day) not in range(1, 32):
            return api_err_return(msg='日（号）不在范围(0~31)内，请检查！')
        else:
            pass

    day_of_week = datas.get('day_of_week') or ''

    if day_of_week:
        if day_of_week.isdigit():
            if int(day_of_week) not in range(0, 7):
                return api_err_return(msg='星期 不在范围(0~6)内，请检查！')
        else:
            if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                return api_err_return(msg='星期 不在范围(mon,tue,wed,thu,fri,sat,sun)内，请检查！')

    hour = datas.get('hour') or ''

    if hour and hour.isdigit():
        if int(hour) not in range(0, 24):
            return api_err_return(msg='小时 不在范围(0~23)内，请检查！')

    minute = datas.get('minute') or ''
    if minute and minute.isdigit():
        if int(minute) not in range(0, 60):
            return api_err_return(msg='分钟 不在范围(0~59)内，请检查！')

    second = datas.get('second') or ''

    if second and second.isdigit():
        if int(second) not in range(0, 60):
            return api_err_return(msg='秒 不在范围(0~59)内，请检查！')

    '''
    判断一下 run_date 必须有个不能为空
    '''
    if not run_date:
        if not day_of_week and not day and not hour and not minute and not second:
            return api_err_return(msg='信息请完整填写！')

    req_url = datas.get('req_url')

    if not req_url:
        return api_err_return(msg='回调URL(req_url)必填！')

    if 'http://' not in req_url and 'https://' not in req_url:
        return api_err_return(msg='回调URL格式有错')

    if not cif:
        cif = CronInfos(task_name=task_name, task_keyword=task_keyword, run_date=run_date, day_of_week=day_of_week,
                        day=day, hour=hour, minute=minute, second=second, req_url=req_url, status=1)
    else:
        cif.task_name = task_name
        cif.task_keyword = task_keyword
        cif.run_date = run_date
        cif.day_of_week = day_of_week
        cif.day = day
        cif.hour = hour
        cif.minute = minute
        cif.second = second
        cif.req_url = req_url
        cif.status = 1

    db.session.add(cif)
    db.session.commit()

    cron_id = cif.id

    cron_datas = {}

    if run_date:
        cron_datas['trigger'] = 'date'
        cron_datas['run_date'] = run_date
    else:
        # 定时的
        cron_datas['trigger'] = 'cron'
        if day_of_week:
            cron_datas['day_of_week'] = day_of_week
        if hour:
            cron_datas['hour'] = hour
        if minute:
            cron_datas['minute'] = minute
        if day:
            cron_datas['day'] = day
        if second and second != '*':
            cron_datas['second'] = second

    scheduler.add_job("cron_%s" % cron_id, func=cron_do, args=[cron_id], replace_existing=True, **cron_datas)

    return 'ok'





