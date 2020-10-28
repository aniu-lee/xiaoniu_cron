#!/bin/bash
pip3 install --upgrade pip
cd /home/www
pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
if [ ! -d "migrations" ];then
python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade
fi
PYTHONIOENCODING=utf-8 gunicorn -c docker_gun.py manage:app
