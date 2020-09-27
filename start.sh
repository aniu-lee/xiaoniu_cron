#!/bin/bash
sudo kill -9 `sudo lsof -t -i:5860`
cd /home/www/xiaoniu_cron
source env/bin/activate
gunicorn -c gun.py manage:app
