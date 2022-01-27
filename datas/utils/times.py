#!/usr/bin/python3 
# -*- coding:utf-8 -*-
import datetime
import time

'''
获取当前时间
'''
def get_now_time(format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format,time.localtime(time.time()))

'''
获取几秒后的时间 seconds days minutes
'''
def get_next_time(format='%Y-%m-%d %H:%M:%S',**ke):
    tiimes = (datetime.datetime.now() + datetime.timedelta(**ke)).strftime(format)
    return tiimes

def get_today(format='%Y-%m-%d'):
    return time.strftime(format,time.localtime(time.time()))