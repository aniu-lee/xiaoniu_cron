#!/bin/bash
if [ ! -d "migrations" ];then
python3.6 manage.py db init
python3.6 manage.py db migrate -m "init"
python3.6 manage.py db upgrade
fi
gunicorn -c docker_gun.py manage:app
