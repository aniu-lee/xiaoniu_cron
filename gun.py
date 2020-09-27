#!/usr/bin/python3
# -*- coding:utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()
errorlog='access_err_log.log'
loglevel = 'error'
bind = '0.0.0.0:5860'
workers=2
worker_class='gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
