# app/database/dbconnection.py
from flask import g
import sqlite3
from app.config import Config


class Database:
    """
    Class for managing connections to multiple SQLite databases within a Flask application.
    Uses the global `g` object to store connections in the request context.
    """
    def __init__(self):
        self.databases = {
            'real_estate': Config.DATABASE_REAL_ESTATE,
            'predictions': Config.DATABASE_PREDICTIONS,
            'users': Config.DATABASE_USERS
        }

    def get_db(self, db_key):
        if db_key not in self.databases:
            raise ValueError(f"Not found: {db_key}")

        if db_key not in g:
            try:
                g.__dict__[db_key] = sqlite3.connect(self.databases[db_key])
                g.__dict__[db_key].row_factory = sqlite3.Row
            except sqlite3.Error as e:
                g.__dict__[db_key] = None
        return g.__dict__[db_key]

    @staticmethod
    def close():
        for key in list(g.__dict__.keys()):
            db = getattr(g, key, None)
            if isinstance(db, sqlite3.Connection):
                db.close()
                del g.__dict__[key]

db_instance = Database()