# app/__init__.py
from flask import Flask
from app.config import Config
from app.auth.routes import login_manager
from flask_mail import Mail


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    mail = Mail(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Авторизуйтесь для подальшого користування сайтом"
    login_manager.login_message_category = 'success'

    from app.routes import predict
    app.register_blueprint(predict)

    from app.auth.routes import auth
    app.register_blueprint(auth)

    return app