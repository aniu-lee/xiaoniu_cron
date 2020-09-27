from apscheduler.schedulers.gevent import GeventScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

from app.CuBackgroundScheduler import CuBackgroundScheduler
from app.CuGeventScheduler import CuGeventScheduler
from config import config

# scheduler=APScheduler()
# scheduler = APScheduler(scheduler=CuGeventScheduler())
scheduler = APScheduler(scheduler=CuBackgroundScheduler())

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    scheduler.app = app

    db.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #接口对接
    from .api import api as apis_bl
    app.register_blueprint(apis_bl, url_prefix='/api')

    return app