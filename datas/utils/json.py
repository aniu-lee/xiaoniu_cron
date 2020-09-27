#coding:utf-8
'''
success return 
'''
from flask import jsonify

def Success(errcode=0,errmsg='good!success!', data=None,url=None, status=200):
    return jsonify({
        'errcode': errcode,
        'errmsg':errmsg,
        'result': data,
        'url':url
    }), status

'''
error 
'''
def Fail(errcode=1,errmsg='error!', data=None,url = None, status=500):
    return jsonify({
        'errcode': errcode,
        'errmsg': errmsg,
        'result': data,
        'url':url
    }), status

def api_return(errcode=0,errmsg='error',data=None):
    if errmsg is None and errcode==1:
        errmsg='error!!'
    if errmsg is None and errcode==0:
        errmsg='success!'

    return jsonify({
        "errcode":errcode,
        "errmsg":errmsg,
        "data":data
    })