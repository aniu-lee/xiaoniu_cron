#!/bin/bash
if [ ! -d "migrations" ];then
  python3.6 manage.py db init
fi
python3.6 manage.py db migrate -m "upgrade"
python3.6 manage.py db upgrade
gunicorn -c docker_gun.py manage:app
