#!/usr/bin/python3 
# -*- coding:utf-8 -*-

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
