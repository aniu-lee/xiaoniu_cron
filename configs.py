#!/usr/bin/python3 
# -*- coding:utf-8 -*-
from configparser import ConfigParser


def configs(key = None):
    cp = ConfigParser()
    cp.read('conf.ini')
    if key:
        return cp.get('default',key)
    is_single = cp.get('default','is_single')
    redis_host = cp.get('default', 'redis_host')
    redis_pwd = cp.get('default', 'redis_pwd')
    redis_db = cp.get('default','redis_db')
    cron_db_url = cp.get('default','cron_db_url')
    cron_job_log_db_url = cp.get('default','cron_job_log_db_url')
    redis_port = cp.get('default','redis_port')
    login_pwd = cp.get('default','login_pwd')
    error_notice_api_key = cp.get('default','error_notice_api_key')

    pz = {
        'is_single':is_single,
        'redis_host':redis_host,
        'redis_pwd':redis_pwd,
        'redis_db': redis_db,
        'cron_db_url': cron_db_url,
        'cron_job_log_db_url':cron_job_log_db_url,
        'redis_port':redis_port,
        'lgoin_pwd':login_pwd,
        'error_notice_url':error_notice_api_key
    }

    return pz