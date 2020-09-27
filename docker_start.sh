#!/bin/bash
pip3 install --upgrade pip

cd /home/www

pip install -r requirements.txt

if [ ! -d "migrations" ];then
python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade
fi
gunicorn -c docker_gun.py manage:app
