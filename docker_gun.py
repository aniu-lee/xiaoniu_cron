#!/usr/bin/python3
# -*- coding:utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()
bind = '0.0.0.0:80'
workers=4
worker_class='gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'