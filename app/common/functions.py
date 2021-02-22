#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from functools import wraps

import redis
import requests
from flask import jsonify, current_app

from configs import configs

'''
推送
https://www.aniulee.com
'''
def wechat_info_err(titile,content=''):
    try:
        api_key = configs('error_notice_api_key')
        if api_key:
            post_url = 'https://api.aniulee.com/blog_api_go/api/v1/push'
            data = {
                'api_key': api_key,
                'content': content,
                'title': titile
            }
            resp = requests.post(post_url, data=data,timeout=2,headers={'user-agent':'XNCron'})
            print(resp.json())
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