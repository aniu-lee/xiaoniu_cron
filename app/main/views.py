# -*- coding:utf-8 -*-
import traceback

from app import scheduler, db
from datas.model.cron_infos import CronInfos
from datas.model.job_log import JobLog
from datas.utils.times import get_now_time
from . import main
from flask import render_template, request, redirect, session, current_app, jsonify, url_for

from ..common.functions import wechat_info_err, web_api_return
from ..crons import cron_do
from ..decorated import login_required


@main.route('/cron_list', methods=['GET', 'POST'])
@main.route('/', methods=['GET', 'POST'])
@login_required
def cron_list():
    keyword = request.args.to_dict()
    page = int(request.args.get('page') or 1)
    task_name = keyword.get('task_name')
    filter_arr = []
    if task_name:
        filter_arr.append(CronInfos.task_name.like('%{}%'.format(task_name)))

    page_data = CronInfos.query.filter(*filter_arr).order_by(db.desc(CronInfos.task_name)).paginate(page=page,
                                                                                                    per_page=20)
    if 'page' in keyword: del keyword['page']
    return render_template("cron_list.html", page_data=page_data, keyword=keyword)


@main.route('/api_doc', methods=['GET', 'POST'])
@login_required
def api_doc():
    return render_template("api_doc.html")


@main.route('/job_log_list', methods=['GET', 'POST'])
@login_required
def job_log_list():
    keywords = request.args.to_dict()

    page = int(request.args.get('page') or 1)
    id = request.args.get('id')

    page_data = JobLog.query.filter(JobLog.cron_info_id == id).order_by(db.desc(JobLog.id)).paginate(page=page,per_page=20)
    if 'page' in keywords:
        del keywords['page']

    return render_template("job_log_list.html", page_data=page_data, keywords=keywords)

@main.route('/job_log_all_list', methods=['GET', 'POST'])
@login_required
def job_log_all_list():
    keywords = request.args.to_dict()

    page = int(request.args.get('page') or 1)

    filter_arr = []
    task_name = keywords.get('task_name')
    if task_name:
        filter_arr.append(CronInfos.task_name.like('{}%'.format(task_name)))
    beg_time = keywords.get('beg_time')
    end_time = keywords.get('end_time')
    if beg_time and end_time:
        filter_arr.append(JobLog.create_time.between(beg_time,end_time))

    page_data = JobLog.query.\
        join(CronInfos,CronInfos.id == JobLog.cron_info_id).\
        filter(*filter_arr).\
        order_by(db.desc(JobLog.id)).\
        add_entity(CronInfos).\
        paginate(page=page,per_page=20)

    if 'page' in keywords:
        del keywords['page']

    return render_template("job_log_all_list.html", page_data=page_data, keywords=keywords)


@main.route('/job_log_delete', methods=['GET', 'POST'])
@login_required
def job_log_delete():
    datas = request.values.to_dict()
    job_log_id = datas.get('job_log_id')
    job_logs = JobLog.query.get(job_log_id)
    if not job_logs:
        return web_api_return(code=1,msg='信息不存在')
    db.session.delete(job_logs)
    db.session.commit()

    return web_api_return(code=0,msg='删除成功')

@main.route('/job_batch_delete', methods=['GET', 'POST'])
@login_required
def job_batch_delete():
    ids = request.form.getlist('id')
    JobLog.query.filter(JobLog.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return web_api_return(code=0, msg='操作成功', url='/job_log_all_list')

@main.route('/cron_add', methods=['GET', 'POST'])
@login_required
def cron_add():
    if request.method == 'POST':
        try:
            datas = request.values.to_dict()
            task_name = datas.get('task_name')
            task_keyword = datas.get('task_keyword')

            if not task_name:
                return web_api_return(code=1,msg='任务名称不能为空')

            _cif = CronInfos.query.filter(CronInfos.task_name == task_name).first()
            if _cif:
                return web_api_return(code=1,msg='任务名称已存在')

            run_date = datas.get('run_date')
            if run_date:
                if run_date < get_now_time('%Y-%m-%d %H:%M'):
                    return web_api_return(code=1,msg='设置的时间已过期，请重新设置')
            day = datas.get('day')

            if day:
                if day.isdigit() and int(day) not in range(1, 32):
                    return web_api_return(code=1,msg='日（号）不在范围内，请检查！')
                else:
                    pass

            day_of_week = datas.get('day_of_week')

            if day_of_week:
                if day_of_week.isdigit():
                    if int(day_of_week) not in range(0, 7):
                        return web_api_return(code=1,msg='星期 不在范围内，请检查！')
                else:
                    if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                        return web_api_return(code=1,msg='星期 不在范围内，请检查！')

            hour = datas.get('hour')

            if hour and hour.isdigit():
                if int(hour) not in range(0, 24):
                    return web_api_return(code=1,msg='小时 不在范围内，请检查！')

            minute = datas.get('minute')
            if minute and minute.isdigit():
                if int(minute) not in range(0, 60):
                    return web_api_return(code=1,msg='分钟 不在范围内，请检查！')

            second = datas.get('second')

            if second and second.isdigit():
                if int(second) not in range(0, 60):
                    return web_api_return(code=1,msg='秒 不在范围内，请检查！')

            ds_ms = datas.get('ds_ms')
            if ds_ms == '1':
                if not run_date:
                    return web_api_return(code=1,msg='时间没设置呢！')
            else:
                if not day_of_week and not day and not hour and not minute and not second:
                    return web_api_return(code=1,msg='请完整填写！')

            req_url = datas.get('req_url')

            if not req_url:
                return web_api_return(code=1,msg='回调URL必填！')

            if 'http://' not in req_url and 'https://' not in req_url:
                return web_api_return(code=1,msg='URL格式有误！')
            cif = CronInfos(task_name=task_name, task_keyword=task_keyword, run_date=run_date, day_of_week=day_of_week,
                            day=day, hour=hour, minute=minute, second=second, req_url=req_url, status=1)

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
            return web_api_return(code=0,msg='添加成功',url='/cron_list')

        except Exception as e:
            trace_info = traceback.format_exc()
            wechat_info_err(str(e), trace_info)
            return web_api_return(code=1, msg=str(e), url='/cron_list')

    return render_template("cron_add.html")


@main.route('/cron_edit', methods=['GET', 'POST'])
@login_required
def cron_edit():
    id = request.values.get('id')
    cif = CronInfos.query.get(id)
    if request.method == 'POST':

        datas = request.values.to_dict()
        ds_ms = datas.get('ds_ms')
        task_name = datas.get('task_name')

        if not task_name:
            return web_api_return(code=1,msg='任务名称不能为空')

        task_keyword = datas.get('task_keyword') or ''

        _cif = CronInfos.query.filter(CronInfos.task_name == task_name,CronInfos.id != datas.get('id')).first()
        if _cif:
            return web_api_return(code=1, msg='任务名称已存在已存在')

        run_date = datas.get('run_date')

        if ds_ms == '2':
            run_date = ''

        if run_date:
            if run_date < get_now_time('%Y-%m-%d %H:%M'):
                return web_api_return(code=1, msg='设置的时间已过期，请重新设置')

        day = datas.get('day')

        if day:
            if day.isdigit() and int(day) not in range(1, 32):
                return web_api_return(code=1, msg='日（号）不在范围内，请检查！')
            else:
                pass

        day_of_week = datas.get('day_of_week')

        if day_of_week:
            if day_of_week.isdigit():
                if int(day_of_week) not in range(0, 7):
                    return web_api_return(code=1, msg='星期 不在范围内，请检查！')
            else:
                if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    return web_api_return(code=1, msg='星期 不在范围内，请检查！')

        hour = datas.get('hour')

        if hour and hour.isdigit():
            if int(hour) not in range(0, 24):
                return web_api_return(code=1, msg='小时 不在范围内，请检查！')

        minute = datas.get('minute')
        if minute and minute.isdigit():
            if int(minute) not in range(0, 60):
                return web_api_return(code=1, msg='分钟 不在范围内，请检查！')

        second = datas.get('second')

        if second and second.isdigit():
            if int(second) not in range(0, 60):
                return web_api_return(code=1, msg='秒 不在范围内，请检查！')

        ds_ms = datas.get('ds_ms')
        if ds_ms == '1':
            if not run_date:
                return web_api_return(code=1, msg='时间没设置呢！')
        else:
            if not day_of_week and not day and not hour and not minute and not second:
                return web_api_return(code=1, msg='请完整填写！')

        req_url = datas.get('req_url')

        if not req_url:
            return web_api_return(code=1, msg='回调URL必填！')

        if 'http://' not in req_url and 'https://' not in req_url:
            return web_api_return(code=1, msg='URL格式有误！')

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

        return web_api_return(code=0, msg='修改成功！',url='/cron_list')

    return render_template("cron_edit.html", cif=cif)


@main.route('/update_status', methods=['GET', 'POST'])
@login_required
def update_status():
    id = request.args.get('id')
    cif = CronInfos.query.get(id)
    if not cif:
        return web_api_return(code=1, msg='项目不存在',url='/cron_list')
    status = cif.status
    _status = 0
    if status == 0:
        _status = 1
        scheduler.resume_job('cron_%s' % cif.id)
    else:
        scheduler.pause_job('cron_%s' % cif.id)
    cif.status = _status
    db.session.add(cif)
    db.session.commit()
    return web_api_return(code=0, msg='操作成功')

@main.route('/cron_del', methods=['GET', 'POST'])
@login_required
def cron_del():
    id = request.args.get('id')
    cif = CronInfos.query.get(id)
    if not cif:
        return web_api_return(code=1, msg='项目不存在', url='/cron_list')
    cron_id = cif.id

    db.session.delete(cif)

    try:
        scheduler.remove_job('cron_%s' % cron_id)
    except:
        pass

    db.session.execute("delete from job_log where cron_info_id='%s'" % cron_id)

    db.session.commit()
    return web_api_return(code=0, msg='操作成功', url='/cron_list')

@main.route('/cron_batch_del', methods=['GET', 'POST'])
@login_required
def cron_batch_del():
    ids = request.form.getlist('id')
    CronInfos.query.filter(CronInfos.id.in_(ids)).delete(synchronize_session=False)
    JobLog.query.filter(JobLog.cron_info_id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    try:
        for cron_id in ids:
            scheduler.remove_job('cron_%s' % cron_id)
    except:
        pass

    return web_api_return(code=0, msg='操作成功', url='/cron_list')

@main.route('/check_pass', methods=['GET', 'POST'])
def check_pass():
    today = get_now_time()
    msg = request.values.get('msg', '')

    if request.method == 'POST':
        try:
            password = request.values.get('password')
            if not password:
                return redirect("/check_pass?msg=密码不能为空")
            login_pwd = current_app.config.get('LOGIN_PWD')
            if not login_pwd:
                return redirect("/check_pass?msg=请联系管理员")
            if login_pwd!=password:
                return redirect("/check_pass?msg=密码有误")
            session['is_login'] = True
            return redirect('/cron_list')
        except:
            return redirect("/check_pass?msg=系统有误,请重新试试")
    return render_template("check_pass.html", msg=msg, today=today)

@main.route('/logout')
def logout():
    session.clear()
    return redirect("/check_pass")