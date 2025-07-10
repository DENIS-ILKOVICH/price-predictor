# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    DEBUG = True

    DATABASE_REAL_ESTATE = os.path.join(BASE_DIR, 'real_estate.db')
    DATABASE_PREDICTIONS = os.path.join(BASE_DIR, 'predictions.db')
    DATABASE_USERS = os.path.join(BASE_DIR, 'users.db')

    SECRET_KEY = os.getenv('SECRET_KEY', 'default')
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'






