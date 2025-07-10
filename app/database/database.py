# app/database/database.py
from flask import g
from app.database.dbconnection import db_instance
from app.routes import predict

@predict.before_request
def before_request():
    g.get_db = db_instance.get_db


@predict.teardown_request
def close_db(error=None):
    db_instance.close()