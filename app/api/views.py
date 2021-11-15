#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from flask import request, current_app

from app import scheduler, db
from app.decorated import api_deal_return, api_err_return
from datas.model.cron_infos import CronInfos
from datas.model.job_log import JobLog
from datas.model.job_log_items import JobLogItems
from . import api
from ..crons import cron_do

@api.route('/test',methods=['GET','POST'])
@api_deal_return
def test():
    print(request.values.to_dict())
    return 'test'

'''
添加（更新）定时
access_token
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
    CRON_CONFIG = current_app.config.get('CRON_CONFIG')

    is_dev = int(CRON_CONFIG.get('is_dev'))

    api_access_token = CRON_CONFIG.get('api_access_token')

    datas = request.values.to_dict()

    task_name = datas.get('task_name')

    task_keyword = datas.get('task_keyword') or ''

    access_token = datas.get('access_token')

    if api_access_token:

        if not access_token:
            return api_err_return(msg='access_token不能为空')

        if api_access_token != access_token:
            return api_err_return(msg='access_token错误')

    if not task_name:
        return api_err_return(msg='任务名称不能为空')

    cif = CronInfos.query.filter(CronInfos.task_name == task_name).first()

    run_date = datas.get('run_date') or ''

    day = datas.get('day') or ''

    if day:
        if day.isdigit() and int(day) not in range(1, 32):
            return api_err_return(code=1, msg='日（号）不在范围内，请检查！')
        else:
            '''
            day 1,2,4-1
            day 1,2,4
            day 1-20
            '''
            day = day.replace('，', ',')
            if day.find(',') != -1 and day.find('-') != -1:
                return api_err_return(code=1, msg='【日】格式有误，同时出现，-')

            if day.find('-') != -1:
                day_s = day.split('-')
                if len(day_s) != 2:
                    return api_err_return(code=1, msg='【日】格式有误哦')

                day_s_1 = day_s[0]
                day_s_2 = day_s[-1]
                if day_s_1.isdigit() is False or day_s_2.isdigit() is False:
                    return api_err_return(code=1, msg='【日】必须是整数')

                if int(day_s_1) >= int(day_s_2):
                    return api_err_return(code=1, msg='【日】前面不能大于后面')

                if int(day_s_1) not in range(1, 32) or int(day_s_2) not in range(1, 32):
                    return api_err_return(code=1, msg='【日】不在范围内')

            elif day.find(',') != -1:
                day_s = day.split(',')
                for item in day_s:
                    if item.isdigit() is False:
                        return api_err_return(code=1, msg='【日】必须是整数')
                    if int(item) not in range(1, 32):
                        return api_err_return(code=1, msg='【日】格式有误，数值不在范围内')
            elif day.find('*') != -1:
                if day.strip() != '*':
                    if day.find('*/') == -1:
                        return api_err_return(code=1, msg='【日】格式有误')
                    if day.split('/')[-1].isdigit() is False:
                        return api_err_return(code=1, msg='【日】格式有误')
            else:
                return api_err_return(code=1, msg='【日】必须是整数')

    day_of_week = datas.get('day_of_week') or ''
    if day_of_week:
        if day_of_week.isdigit():
            if int(day_of_week) not in range(0, 7):
                return api_err_return(code=1, msg='【星期】 不在范围内，请检查！')
        else:
            # 1,2,4
            # 1-3
            day_of_week = day_of_week.replace('，', ',')
            if day_of_week.find(',') != -1 and day_of_week.find('-') != -1:
                return api_err_return(code=1, msg='【星期】格式有误，同时出现，-')

            if day_of_week.find('-') != -1:
                day_s = day_of_week.split('-')
                if len(day_s) != 2:
                    return api_err_return(code=1, msg='【星期】格式有误哦')

                day_s_1 = day_s[0]
                day_s_2 = day_s[-1]
                if day_s_1.isdigit() is False or day_s_2.isdigit() is False:
                    return api_err_return(code=1, msg='【星期】必须是整数')

                if int(day_s_1) >= int(day_s_2):
                    return api_err_return(code=1, msg='【星期】前面不能大于后面')

                if int(day_s_1) not in range(0, 7) or int(day_s_2) not in range(0, 7):
                    return api_err_return(code=1, msg='【星期】不在范围内')

            elif day_of_week.find(',') != -1:
                day_s = day_of_week.split(',')
                for item in day_s:
                    if item.isdigit() is False:
                        if item not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                            return api_err_return(code=1, msg='【星期】 不在范围内，请检查！')
                    else:
                        if int(item) not in range(0, 7):
                            return api_err_return(code=1, msg='【星期】格式有误，数值不在范围内')

            elif day_of_week.find('*') != -1:
                if day_of_week.strip() != '*':
                    if day_of_week.find('*/') == -1:
                        return api_err_return(code=1, msg='【星期】格式有误')
                    if day_of_week.split('/')[-1].isdigit() is False:
                        return api_err_return(code=1, msg='【星期】格式有误')
            else:
                if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    return api_err_return(code=1, msg='【星期】 不在范围内，请检查！')

    '''
    0-23
    '''
    hour = datas.get('hour') or ''
    if hour:
        if hour.isdigit():
            if int(hour) not in range(0, 24):
                return api_err_return(code=1, msg='【小时】 不在范围内，请检查！')
        else:
            # 1,2,4
            # 1-3
            hour = hour.replace('，', ',')
            if hour.find(',') != -1 and hour.find('-') != -1:
                return api_err_return(code=1, msg='【小时】格式有误，同时出现，-')

            if hour.find('-') != -1:
                day_s = hour.split('-')
                if len(day_s) != 2:
                    return api_err_return(code=1, msg='【小时】格式有误哦')

                day_s_1 = day_s[0]
                day_s_2 = day_s[-1]
                if day_s_1.isdigit() is False or day_s_2.isdigit() is False:
                    return api_err_return(code=1, msg='【小时】必须是整数')

                if int(day_s_1) >= int(day_s_2):
                    return api_err_return(code=1, msg='【小时】前面不能大于后面')

                if int(day_s_1) not in range(0, 24) or int(day_s_2) not in range(0, 24):
                    return api_err_return(code=1, msg='【小时】不在范围内')

            elif hour.find(',') != -1:
                day_s = hour.split(',')
                for item in day_s:
                    if item.isdigit() is False:
                        return api_err_return(code=1, msg='【小时】必须是整数！')
                    else:
                        if int(item) not in range(0, 7):
                            return api_err_return(code=1, msg='【小时】格式有误，数值不在范围内')

            elif hour.find('*') != -1:
                if hour.strip() != '*':
                    if hour.find('*/') == -1:
                        return api_err_return(code=1, msg='【小时】格式有误')
                    if hour.split('/')[-1].isdigit() is False:
                        return api_err_return(code=1, msg='【小时】格式有误')
            else:
                return api_err_return(code=1, msg='【小时】必须是整数')

    '''
    0-59
    '''
    minute = datas.get('minute') or ''
    if minute:
        if minute.isdigit():
            if int(minute) not in range(0, 60):
                return api_err_return(code=1, msg='【分】 不在范围内，请检查！')
        else:
            # 1,2,4
            # 1-3
            minute = minute.replace('，', ',')
            if minute.find(',') != -1 and minute.find('-') != -1:
                return api_err_return(code=1, msg='【分】格式有误，同时出现，-')

            if minute.find('-') != -1:
                day_s = minute.split('-')
                if len(day_s) != 2:
                    return api_err_return(code=1, msg='【分】格式有误哦')

                day_s_1 = day_s[0]
                day_s_2 = day_s[-1]
                if day_s_1.isdigit() is False or day_s_2.isdigit() is False:
                    return api_err_return(code=1, msg='【分】必须是整数')

                if int(day_s_1) >= int(day_s_2):
                    return api_err_return(code=1, msg='【分】前面不能大于后面')

                if int(day_s_1) not in range(0, 60) or int(day_s_2) not in range(0, 60):
                    return api_err_return(code=1, msg='【分】不在范围内')

            elif minute.find(',') != -1:
                day_s = minute.split(',')
                for item in day_s:
                    if item.isdigit() is False:
                        return api_err_return(code=1, msg='【分】必须是整数！')
                    else:
                        if int(item) not in range(0, 60):
                            return api_err_return(code=1, msg='【分】格式有误，数值不在范围内')

            elif minute.find('*') != -1:
                if minute.strip() != '*':
                    if minute.find('*/') == -1:
                        return api_err_return(code=1, msg='【分】格式有误')
                    if minute.split('/')[-1].isdigit() is False:
                        return api_err_return(code=1, msg='【分】格式有误')
            else:
                return api_err_return(code=1, msg='【分】必须是整数')

    second = datas.get('second') or ''
    if second:
        if second.isdigit():
            if int(second) not in range(0, 60):
                return api_err_return(code=1, msg='【秒】 不在范围内，请检查！')
        else:
            second = second.replace('，', ',')
            if second.find(',') != -1 and second.find('-') != -1:
                return api_err_return(code=1, msg='【秒】格式有误，同时出现，-')

            if second.find('-') != -1:
                day_s = second.split('-')
                if len(day_s) != 2:
                    return api_err_return(code=1, msg='【秒】格式有误哦')

                day_s_1 = day_s[0]
                day_s_2 = day_s[-1]
                if day_s_1.isdigit() is False or day_s_2.isdigit() is False:
                    return api_err_return(code=1, msg='【秒】必须是整数')

                if int(day_s_1) >= int(day_s_2):
                    return api_err_return(code=1, msg='【秒】前面不能大于后面')

                if int(day_s_1) not in range(0, 60) or int(day_s_2) not in range(0, 60):
                    return api_err_return(code=1, msg='【秒】不在范围内')

            elif second.find(',') != -1:
                day_s = second.split(',')
                for item in day_s:
                    if item.isdigit() is False:
                        return api_err_return(code=1, msg='【秒】必须是整数！')
                    else:
                        if int(item) not in range(0, 60):
                            return api_err_return(code=1, msg='【秒】格式有误，数值不在范围内')

            elif second.find('*') != -1:
                if second.strip() != '*':
                    if second.find('*/') == -1:
                        return api_err_return(code=1, msg='【秒】格式有误')
                    if second.split('/')[-1].isdigit() is False:
                        return api_err_return(code=1, msg='【秒】格式有误')
            else:
                return api_err_return(code=1, msg='【秒】必须是整数')

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

    if is_dev == 1:second=''

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

'''
更新状态
task_name 任务名称
access_token 
status
'''
@api.route('/cron/status',methods=['GET','POST'])
@api_deal_return
def cron_status():
    datas = request.values.to_dict()

    CRON_CONFIG = current_app.config.get('CRON_CONFIG')

    api_access_token = CRON_CONFIG.get('api_access_token')

    task_name = datas.get('task_name')

    access_token = datas.get('access_token')

    status = datas.get('status')

    if status:
        try:
            if int(status) not in [0,1]:
                return api_err_return(msg='status只能0或者1')
        except:
            return api_err_return(msg='status只能0或者1')

    if api_access_token:

        if not access_token:
            return api_err_return(msg='access_token不能为空')

        if api_access_token != access_token:
            return api_err_return(msg='access_token错误')

    if not task_name:
        return api_err_return(msg='任务名称不能为空')

    ci = CronInfos.query.filter(CronInfos.task_name == task_name).first()
    if not ci:
        return api_err_return(msg='任务不存在')

    if ci.status == -1:
        return api_err_return(msg='任务已结束，不能再操作，只能重新更新')

    if not status:
        #0停止1运行中
        if ci.status == 0:
            #开启
            ci.status = 1
            scheduler.resume_job('cron_%s' % ci.id)
        else:
            ci.status = 0
            #关闭
            scheduler.pause_job('cron_%s' % ci.id)
    else:
        if int(status) == 0 and ci.status != 0:
            ci.status = 0
            # 关闭
            scheduler.pause_job('cron_%s' % ci.id)

        if int(status) == 1 and ci.status !=1:
            ci.status = 1
            scheduler.resume_job('cron_%s' % ci.id)

    db.session.add(ci)
    db.session.commit()

    return 'ok'

'''
上传执行记录
xiaoniu_cron_log_id
content
'''
@api.route('/cron/add_log',methods=['GET','POST'])
@api_deal_return
def cron_add_log():
    datas = request.values.to_dict()

    CRON_CONFIG = current_app.config.get('CRON_CONFIG')

    api_access_token = CRON_CONFIG.get('api_access_token')

    access_token = datas.get('access_token')

    xiaoniu_cron_log_id = datas.get('xiaoniu_cron_log_id')

    if api_access_token:

        if not access_token:
            return api_err_return(msg='access_token不能为空')

        if api_access_token != access_token:
            return api_err_return(msg='access_token错误')

    if not xiaoniu_cron_log_id:
        return api_err_return(msg='xiaoniu_cron_log_id 必传哦！')

    content = datas.get('content')
    if not content:
        return api_err_return(msg='日志内容不能为空')

    jl = JobLog.query.filter(JobLog.log_id == xiaoniu_cron_log_id).first()
    if not jl:
        return api_err_return(msg='xiaoniu_cron_log_id 不存在')

    jli = JobLogItems(log_id=xiaoniu_cron_log_id,content=content)

    db.session.add(jli)

    db.session.commit()

    return 'ok'




