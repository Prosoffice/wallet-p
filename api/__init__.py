import os
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail

from api.config import config
# from api.core import all_exception_handler

mail = Mail()


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    # check environment variables to see which config to load
    env = os.environ.get("FLASK_ENV", "dev")
    # for configuration options, look at api/config.py
    if test_config:
        app.config.from_mapping(**test_config)
    else:
        app.config.from_object(config[env])  # config dict is from api/config.py

    # logging
    formatter = RequestFormatter(
        "%(asctime)s %(remote_addr)s: requested %(url)s: %(levelname)s in [%(module)s: %(lineno)d]: %(message)s"
    )
    if app.config.get("LOG_FILE"):
        fh = logging.FileHandler(app.config.get("LOG_FILE"))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        app.logger.addHandler(fh)

    strm = logging.StreamHandler()
    strm.setLevel(logging.DEBUG)
    strm.setFormatter(formatter)

    app.logger.addHandler(strm)
    app.logger.setLevel(logging.DEBUG)

    root = logging.getLogger("core")
    root.addHandler(strm)

 

    # register sqlalchemy to this app
    from api.models import db, ma, bcrypt, jwt, rbac 

    db.init_app(app)
    ma.init_app(app)  # initializing Marshmellow
    bcrypt.init_app(app)
    Migrate(app, db)
    app.config["JWT_SECRET_KEY"] = "QWERTYUIOPLKJHGFDSZXCVBNM.234567SFGSGSGSbfggsgsgss"
    jwt.init_app(app)
    mail.init_app(app)


    # import and register blueprints
    from api.views import main
    from api.views.transactions import transactions
    from api.views.admin import admin


    app.register_blueprint(main.main)
    app.register_blueprint(transactions, url_prefix='/transactions')
    app.register_blueprint(admin, url_prefix="/admin")

    return app