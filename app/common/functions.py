#!/usr/bin/python3 
# -*- coding:utf-8 -*-
import hashlib
import json
import os
import time
from functools import wraps

import redis
import requests
from flask import jsonify, current_app

from configs import configs
from datas.utils.times import get_now_time

'''
md5加密
'''
def md5(str=''):
    m = hashlib.md5()
    m.update(str.encode('utf8'))
    return m.hexdigest()

def get_xiaoniu_cron_sign(data={},api_key=''):
    key_data=[d for d in sorted(data,reverse=False)]
    values = '&&'.join("%s=%s" %(v,data[v]) for v in key_data if data[v])+"&&api_key=" + api_key
    return md5(values)

'''
推送
'''
def wechat_info_err(titile,content=''):
    try:
        content = '【小牛定时任务推送】\n{}\n{}\n{}'.format(get_now_time(),titile,content)
        send_text(content=content)
    except Exception as e:
        current_app.logger.error("推送有BUG【%s】" % str(e))

def web_api_return(code,msg='ok',url=''):
    return jsonify({
        'errcode': code,
        'errmsg': msg,
        'url': url
    })

def dict2string(dict_data,separator = "&&"):
    dd = separator.join("%s=%s" %(v,dict_data[v]) for v in dict_data)
    return dd

'''
缓存
key
value 值
timeout 过期时间
'''
def caches(key,value=None,timeout=-1):
    BASEDIR = current_app.config.get('BASEDIR')
    if not os.path.isdir(os.path.join(BASEDIR,'caches')):
        os.mkdir(os.path.join(BASEDIR,'caches'))

    files = os.path.join(BASEDIR,"caches/%s.log" % key)

    if value is None and key:
        if not os.path.isfile(files):
            return None
        with open(files,'r') as f:
            data = json.loads(f.read())
            _timeout = data.get('timeout')
            if int(_timeout) == -1:
                return data.get('value')
            #过期
            if int(_timeout) < int(time.time()):
                os.remove(files)
                return None
            return data.get('value')

    if key and value:
        with open(files, mode="w", encoding="utf-8") as fd:
            if timeout < int(time.time()) and timeout > 0:
                timeout = int(time.time()) + timeout
            value = json.dumps({
                'value': value,
                'timeout':timeout
            },ensure_ascii=False)
            fd.write(value)

    return 'ok'

def get_access_token(corpid,corpsecret):
    cache_access_token = caches('qywechat_access_token')
    if not cache_access_token:
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (corpid, corpsecret)
        req = requests.get(url)
        ret = req.json()
        if 'access_token' in ret:
            cache_access_token = ret.get('access_token')
            caches('qywechat_access_token',cache_access_token,timeout=2*60*60 - 60)
    return cache_access_token

def qyweixin_push(content):
    config = current_app.config.get('CRON_CONFIG')
    corpid = config.get('qywechat_corpid')
    corpsecret = config.get('qywechat_corpsecret')
    agentid = config.get('qywechat_agentid')
    if not corpid and not corpsecret and not agentid:
        return
    access_token = get_access_token(corpid=corpid, corpsecret=corpsecret)
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % access_token
    data = {
        "touser": "@all",
        "toparty": "@all",
        "totag": "@all",
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": content
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    req = requests.post(url=url, data=json.dumps(data))
    current_app.logger.info(req.json())

def web_hook_push(content):
    config = current_app.config.get('CRON_CONFIG')
    error_web_hook = config.get('error_web_hook')
    if not error_web_hook:
        return

    # 判断是否合法
    if error_web_hook.find('http') !=0:
        current_app.logger.error("web_hook有误")
        return

    try:
        if "{{content}}" in error_web_hook:
            error_web_hook = error_web_hook.replace("{{content}}", content)
            requests.get(error_web_hook)
        else:
            requests.get(error_web_hook,params={'content':content})
    except Exception as e:
        current_app.logger.error("web_hook请求有误:%s" % str(e))

def send_text(content):
    qyweixin_push(content=content)
    web_hook_push(content=content)

# 单节点任务装饰器，被装饰的任务在分布式多节点下同一时间只能运行一次
def single_task():
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            task = func.__name__

            config = configs()

            is_single = config.get('is_single')

            if is_single and is_single != '1':

                if config.get('redis_pwd'):
                    pool = redis.ConnectionPool(host=config.get('redis_host'), port=config.get('redis_port') or 6379,
                                                db=config.get('redis_db') or 0, password=config.get('redis_pwd'))
                else:
                    pool = redis.ConnectionPool(host=config.get('redis_host'), port=config.get('redis_port') or 6379,
                                                db=config.get('redis_db') or 0)

                r = redis.Redis(connection_pool=pool)

                task_id = args[0] if args else ''

                task_name = "task:%s:%s" % (task,task_id)
                _result = r.get(task_name)

                if not _result:
                    r.set(task_name,1,ex=2*60)
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        raise e
                    finally:
                        r.delete(task_name)
                else:
                    return
            else:
                result = func(*args, **kwargs)
                return result
        return inner
    return wrap