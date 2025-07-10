#app/auth/models/models.py
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime


class Users:
    def __init__(self, db):
        if db is None:
            raise ValueError("Database connection is not established.")
        self.__db = db
        self.__cur = db.cursor()

    def get_user_by_email(self, mail):
        try:
            self.__cur.execute('SELECT * FROM users WHERE email = ? LIMIT 1', (mail.lower(),))
            res = self.__cur.fetchone()
            if res:
                return res
        except Exception as e:
            return None


    def adduser(self, name, email, hpsw):
        try:
            self.__cur.execute("SELECT COUNT(*) FROM users WHERE email LIKE ?", (email,))
            res = self.__cur.fetchone()
            if res[0] > 0:
                return False

            last_id = self.__cur.execute('select id from users order by id desc limit 1').fetchone()

            if last_id:
                next_id = str(int(last_id[0]) + 1)
            else:
                next_id = '1'

            current_datetime = datetime.now()
            tm = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            email_data = email.lower()

            self.__cur.execute('INSERT INTO users (id, name, email, password, time, status) '
                               'VALUES (?, ?, ?, ?, ?, ?)', (next_id, name, email_data, hpsw, tm, 1))
            self.__db.commit()

            id_user = self.__cur.execute('SELECT * FROM users WHERE email = ? LIMIT 1', (email_data,)).fetchone()

            return id_user
        except Exception as e:
            return None


    def generate_remember_token(self, secret_key, user_id):

        serializer = URLSafeTimedSerializer(secret_key)
        data = {"user_id": user_id}
        token = serializer.dumps(data)

        try:
            self.__cur.execute('UPDATE users SET remember_token = ? WHERE id = ?', (token, user_id))
            self.__db.commit()
        except Exception as e:
            print(e)
        return token

    def verify_remember_token(self, token, secret_key):
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            data = serializer.loads(token)
            user_id = data['user_id']

            user = self.__cur.execute('select * from users where id = ? LIMIT 1', (user_id,)).fetchone()
            if user:
                return user
        except Exception:
            return None

    def remember_token_none(self, user_id):
        token = None
        try:
            self.__cur.execute('UPDATE users SET remember_token = ? WHERE id = ?', (token, user_id))
            self.__db.commit()
            return True
        except Exception as e:
            return None


    def getuser(self, user_id):
        try:
            self.__cur.execute('SELECT * FROM users WHERE id = ? LIMIT 1', (user_id,))
            res = self.__cur.fetchone()
            if res:
                return res
            else:
                return False
        except Exception as e:
            return None


    def change_email(self, user_id, new_email):
        try:
            self.__cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            res = self.__cur.fetchone()
            if not res:
                return False

            self.__cur.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
            self.__db.commit()
            return True

        except Exception as e:
            return None


    def change_passw(self, user_id, new_psw):
        try:
            self.__cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_psw, user_id))
            self.__db.commit()
            return True

        except Exception as e:
            return None

    def change_name(self, user_id, new_name):
        try:
            self.__cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
            self.__db.commit()
            return True

        except Exception as e:
            return None