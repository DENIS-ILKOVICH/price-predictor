#app/auth/src/user_login/user_login.py
from flask_login import UserMixin

class UserLogin(UserMixin):
    """
    Class for managing user data in session, implementing the Flask-Login interface (UserMixin).

    Attributes:
        __user (dict): Dictionary with user data retrieved from the database or passed directly.

    Methods:
        fromDB(user_id, db): Loads user data from the database by user_id and stores it in the object.
        create(user): Initializes the user object with data from the given user dictionary.
        get_id(): Returns the user ID as a string (required method for Flask-Login).
        get_name(): Returns the user's name.
        get_status(): Returns the user's numeric status (e.g., 0 — admin).
        is_admin(): Checks if the user is an administrator (status == 0).
        get_password(): Returns the user's password (usually hashed).
        get_email(): Returns the user's email.
    """
    def fromDB(self, user_id, db):
        self.__user = db.getuser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])

    def get_status(self):
        return int(self.__user['status'])

    def is_admin(self):
        return self.__user['status'] == 0

    def get_password(self):
        return str(self.__user['password'])

    def get_email(self):
        return str(self.__user['email'])
