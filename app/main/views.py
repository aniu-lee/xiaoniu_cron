# -*- coding:utf-8 -*-
import traceback

import records

from app import scheduler, db
from datas.model.cron_infos import CronInfos
from datas.model.job_log import JobLog
from datas.utils.times import get_now_time
from . import main
from flask import render_template, request, redirect, session, current_app, jsonify, url_for

from ..common.functions import wechat_info_err
from ..crons import cron_do


@main.route('/cron_list', methods=['GET', 'POST'])
@main.route('/', methods=['GET', 'POST'])
def cron_list():
    keyword = request.args.to_dict()
    if 'is_pass' not in session:
        return redirect(url_for('main.check_pass',msg='需要验证动态口令'))
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
def api_doc():
    return render_template("api_doc.html")


@main.route('/job_log_list', methods=['GET', 'POST'])
def job_log_list():
    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证动态口令')

    keywords = request.args.to_dict()

    page = int(request.args.get('page') or 1)
    id = request.args.get('id')

    page_data = JobLog.query.filter(JobLog.cron_info_id == id).order_by(db.desc(JobLog.id)).paginate(page=page,per_page=20)
    if 'page' in keywords:
        del keywords['page']

    return render_template("job_log_list.html", page_data=page_data, keywords=keywords)

@main.route('/job_log_all_list', methods=['GET', 'POST'])
def job_log_all_list():
    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证动态口令')

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


@main.route('/cron_add', methods=['GET', 'POST'])
def cron_add():
    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证动态口令')

    if request.method == 'POST':
        try:
            if 'is_admin' not in session:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '您没有权限操作',
                    'url': ''
                })

            datas = request.values.to_dict()
            task_name = datas.get('task_name')
            task_keyword = datas.get('task_keyword')

            if not task_name:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '任务名称不能为空',
                    'url': ''
                })

            _cif = CronInfos.query.filter(CronInfos.task_name == task_name).first()
            if _cif:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '任务名称已存在',
                    'url': ''
                })

            run_date = datas.get('run_date')
            if run_date:
                if run_date < get_now_time('%Y-%m-%d %H:%M'):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '设置的时间已过期，请重新设置',
                        'url': ''
                    })
            day = datas.get('day')

            if day:
                if day.isdigit() and int(day) not in range(1, 32):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '日（号）不在范围内，请检查！',
                        'url': ''
                    })
                else:
                    pass

            day_of_week = datas.get('day_of_week')

            if day_of_week:
                if day_of_week.isdigit():
                    if int(day_of_week) not in range(0, 7):
                        return jsonify({
                            'errcode': 1,
                            'errmsg': '星期 不在范围内，请检查！',
                            'url': ''
                        })
                else:
                    if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                        return jsonify({
                            'errcode': 1,
                            'errmsg': '星期 不在范围内，请检查！',
                            'url': ''
                        })

            hour = datas.get('hour')

            if hour and hour.isdigit():
                if int(hour) not in range(0, 24):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '小时 不在范围内，请检查！',
                        'url': ''
                    })

            minute = datas.get('minute')
            if minute and minute.isdigit():
                if int(minute) not in range(0, 60):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '分钟 不在范围内，请检查！',
                        'url': ''
                    })

            second = datas.get('second')

            if second and second.isdigit():
                if int(second) not in range(0, 60):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '秒 不在范围内，请检查！',
                        'url': ''
                    })

            ds_ms = datas.get('ds_ms')
            if ds_ms == '1':
                if not run_date:
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '时间没设置呢！',
                        'url': ''
                    })
            else:
                if not day_of_week and not day and not hour and not minute and not second:
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '请完整填写！',
                        'url': ''
                    })

            req_url = datas.get('req_url')

            if not req_url:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '回调URL必填！',
                    'url': ''
                })

            if 'http://' not in req_url and 'https://' not in req_url:
                return jsonify({
                    'errcode': 1,
                    'errmsg': 'URL格式有误！',
                    'url': ''
                })
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

            return jsonify({
                'errcode': 0,
                'errmsg': '添加成功',
                'url': '/cron_list'
            })
        except Exception as e:
            trace_info = traceback.format_exc()
            wechat_info_err(str(e), trace_info)
            return jsonify({
                'errcode': 1,
                'errmsg': str(e),
                'url': '/cron_list'
            })

    return render_template("cron_add.html")


@main.route('/cron_edit', methods=['GET', 'POST'])
def cron_edit():
    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证密码+两位动态密码')

    id = request.values.get('id')
    cif = CronInfos.query.get(id)
    if request.method == 'POST':
        if 'is_admin' not in session:
            return jsonify({
                'errcode': 1,
                'errmsg': '您没有权限操作',
                'url': ''
            })

        datas = request.values.to_dict()
        ds_ms = datas.get('ds_ms')
        task_name = datas.get('task_name')

        if not task_name:
            return jsonify({
                'errcode': 1,
                'errmsg': '任务名称不能为空',
                'url': ''
            })

        task_keyword = datas.get('task_keyword') or ''

        _cif = CronInfos.query.filter(CronInfos.task_name == task_name,CronInfos.id != datas.get('id')).first()
        if _cif:
            return jsonify({
                'errcode': 1,
                'errmsg': '任务名称已存在已存在',
                'url': ''
            })

        run_date = datas.get('run_date')

        if ds_ms == '2':
            run_date = ''

        if run_date:
            if run_date < get_now_time('%Y-%m-%d %H:%M'):
                return jsonify({
                    'errcode': 1,
                    'errmsg': '设置的时间已过期，请重新设置',
                    'url': ''
                })

        day = datas.get('day')

        if day:
            if day.isdigit() and int(day) not in range(1, 32):
                return jsonify({
                    'errcode': 1,
                    'errmsg': '日（号）不在范围内，请检查！',
                    'url': ''
                })
            else:
                pass

        day_of_week = datas.get('day_of_week')

        if day_of_week:
            if day_of_week.isdigit():
                if int(day_of_week) not in range(0, 7):
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '星期 不在范围内，请检查！',
                        'url': ''
                    })
            else:
                if day_of_week not in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    return jsonify({
                        'errcode': 1,
                        'errmsg': '星期 不在范围内，请检查！',
                        'url': ''
                    })

        hour = datas.get('hour')

        if hour and hour.isdigit():
            if int(hour) not in range(0, 24):
                return jsonify({
                    'errcode': 1,
                    'errmsg': '小时 不在范围内，请检查！',
                    'url': ''
                })

        minute = datas.get('minute')
        if minute and minute.isdigit():
            if int(minute) not in range(0, 60):
                return jsonify({
                    'errcode': 1,
                    'errmsg': '分钟 不在范围内，请检查！',
                    'url': ''
                })

        second = datas.get('second')

        if second and second.isdigit():
            if int(second) not in range(0, 60):
                return jsonify({
                    'errcode': 1,
                    'errmsg': '秒 不在范围内，请检查！',
                    'url': ''
                })

        ds_ms = datas.get('ds_ms')
        if ds_ms == '1':
            if not run_date:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '时间没设置呢！',
                    'url': ''
                })
        else:
            if not day_of_week and not day and not hour and not minute and not second:
                return jsonify({
                    'errcode': 1,
                    'errmsg': '请完整填写！',
                    'url': ''
                })

        req_url = datas.get('req_url')

        if not req_url:
            return jsonify({
                'errcode': 1,
                'errmsg': '回调URL必填！',
                'url': ''
            })

        if 'http://' not in req_url and 'https://' not in req_url:
            return jsonify({
                'errcode': 1,
                'errmsg': 'URL格式有误！',
                'url': ''
            })
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

        return jsonify({
            'errcode': 0,
            'errmsg': '修改成功',
            'url': '/cron_list'
        })
    return render_template("cron_edit.html", cif=cif)


@main.route('/update_status', methods=['GET', 'POST'])
def update_status():

    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证动态口令')

    if 'is_admin' not in session:
        return jsonify({
            'errcode':1,
            'errmsg':'您没有权限操作',
            'url':''
        })

    id = request.args.get('id')
    cif = CronInfos.query.get(id)
    if not cif:
        return jsonify({
            'errcode': 1,
            'errmsg': '项目不存在',
            'url': '/cron_list'
        })
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

    return jsonify({
        'errcode': 0,
        'errmsg': '操作成功',
        'url': ''
    })


@main.route('/cron_del', methods=['GET', 'POST'])
def cron_del():
    if 'is_pass' not in session:
        return redirect('/check_pass?msg=需要验证密码')

    if 'is_admin' not in session:
        return jsonify({
            'errcode':1,
            'errmsg':'您没有权限操作',
            'url':''
        })
    id = request.args.get('id')
    cif = CronInfos.query.get(id)
    if not cif:
        return jsonify({
            'errcode': 1,
            'errmsg': '项目不存在',
            'url': ''
        })

    cron_id = cif.id

    db.session.delete(cif)

    try:
        scheduler.remove_job('cron_%s' % cron_id)
    except:
        pass

    db.session.execute("delete from job_log where cron_info_id='%s'" % cron_id)

    db.session.commit()

    return jsonify({
        'errcode': 0,
        'errmsg': '操作成功',
        'url': '/cron_list'
    })


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
            if len(password) > len(login_pwd) +2:
                return redirect("/check_pass?msg=密码格式有误")
            if len(password) < len(login_pwd):
                return redirect("/check_pass?msg=密码格式有误")
            if len(password) == len(login_pwd):
                if password == login_pwd:
                    session['is_pass'] = 1
                    return redirect("/cron_list")
            _pass = password[0:len(login_pwd)]
            my = password[len(login_pwd)-len(password):]
            if _pass == login_pwd:
                session['is_pass'] = 1
            ctt = int(get_now_time('%M'))
            try:
                if int(my) == ctt:
                    session['is_admin'] = 1
            except:
                pass
            return redirect('/cron_list')
        except:
            return redirect("/check_pass?msg=系统有误,请重新试试")
    return render_template("check_pass.html", msg=msg, today=today)

@main.route('/logout')
def logout():
    session.clear()
    return redirect("/cron_list")