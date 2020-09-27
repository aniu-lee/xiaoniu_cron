#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from functools import wraps

from datas.utils.json import api_return

def api_err_return(code=1,msg='',data=''):
    return code,msg,data

'''
接口 api返回
'''
def api_deal_return(func):
    @wraps(func)
    def gen_status(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if type(result)==str:
                return api_return(errcode=0,errmsg=result)
            if type(result)==list or type(result)==dict:
                return api_return(errcode=0,errmsg='success',data=result)
            if type(result)==tuple:
                if len(result)==2:
                    errmsg=result[0]
                    if errmsg is None or errmsg=="":
                        errmsg='success'
                    return api_return(errcode=0, errmsg=errmsg, data=result[1])
                else:
                    return api_return(errcode=result[0],errmsg=result[1],data=result[2])
        except Exception as e:
            error = str(e)
            return api_return(errcode=1,errmsg=error)
    return gen_status