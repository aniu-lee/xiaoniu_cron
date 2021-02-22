import logging
from logging.handlers import TimedRotatingFileHandler

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

    logging.basicConfig(level=logging.ERROR)

    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")

    info_handler = TimedRotatingFileHandler("%s/datas/logs/info.log" % config[config_name].BASEDIR, when="H",
                                            interval=1, backupCount=7, encoding="UTF-8", delay=False,
                                            utc=True)
    # info_handler.setLevel(logging.INFO)
    info_handler.filter = lambda record: record.levelno == logging.INFO
    app.logger.addHandler(info_handler)
    info_handler.setFormatter(formatter)

    error_handler = TimedRotatingFileHandler("%s/datas/logs/error.log" % config[config_name].BASEDIR, when="D",
                                             interval=1, backupCount=15, encoding="UTF-8", delay=False,
                                             utc=True)
    error_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_handler)
    error_handler.setFormatter(formatter)

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