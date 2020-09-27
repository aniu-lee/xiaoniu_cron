#!/usr/bin/python3 
# -*- coding:utf-8 -*-
import json


import redis
from flask import current_app

'''
http://www.cnblogs.com/melonjiang/p/5342505.html
自定义缓存redis
author:aniulee
time:2018-10-17
'''
class RedisCache(object):
    def __init__(self,host=None,port=None,db=None,password=None,prefix=None):

        if not hasattr(RedisCache, 'pool'):
            RedisCache.create_pool(host,port,db,password)
        self.prefix = prefix
        self._connection = redis.Redis(connection_pool=RedisCache.pool)

    @staticmethod
    def create_pool(host,port,db,password):
        if host is None:
            host = current_app.config.get('MY_REDIS_HOST')
        if password is None:
            password = current_app.config.get('MY_REDIS_PASSWORD',None)

        port = port or 6379
        db = db or 0
        if password:
            RedisCache.pool = redis.ConnectionPool(host=host,port=port,db=db,password=password)
        else:
            RedisCache.pool = redis.ConnectionPool(host=host, port=port, db=db)

    '''
    redis 对象 可以用来拓展
    '''
    def getInstance(self):
        return self._connection

    '''
    添加
    timeout 秒
    '''
    def set(self, key, value,timeout=None):
        prefix = self.prefix or ''
        value = json.dumps({
            'value':value
        })
        return self._connection.set("%s%s" % (prefix,key), value,ex=timeout)

    '''
    与set一模一样
    '''
    def add(self,key,value,timeout=None):
        return self.set(key,value,timeout)

    '''
    获取
    '''
    def get(self, key):
        prefix = self.prefix or ''
        ret_data = self._connection.get("%s%s" % (prefix,key))
        if ret_data is not None:
            if isinstance(ret_data,bytes):
                ret = ret_data.decode('utf-8')
                ret = json.loads(ret)
                return ret['value']
        return ret_data

    '''
    单个删除
    '''
    def delete(self,key):
        return self._connection.delete(key)

    '''
    清除所有
    '''
    def clear(self,prefix=None):
        if prefix is None:
            prefix = self.prefix or '*'
        keys = self._connection.keys(pattern='%s*' % prefix)
        if keys:
            for kk in keys:
                kk = kk.decode('utf-8')
                self.getInstance().delete(kk)
        return True

if __name__ == '__main__':
    pass
    # red = RedisCache(host='127.0.0.1',db=0,prefix='flask_blg')

    # red.set('cc',2,timeout=120)
    # red.set('aa',3,timeout=120)
    # red.set('bb',4,timeout=60)
    # red.clear()
    # print(red.delete('aniulee'))
    # print(red.get('aniulee'))
    # print(red.get('cc'))
    # red.set('test','1',timeout=10)
    # ret = red.get('test')
    # print(ret)
    # print(type(ret))