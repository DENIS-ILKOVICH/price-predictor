# app/models/users/models.py
class UserDB:
    def __init__(self, db):
        if db is None:
            raise ValueError("Database connection is not established.")
        self.__db = db
        self.__cur = db.cursor()

    def add_user_predictions(self, user_id, req_id, pr_id):
        try:
            user_id, req_id, pr_id = int(user_id), int(req_id), int(pr_id)
            self.__cur.execute('''
                INSERT INTO user_predictions (user_id, request_id, prediction_id)
                VALUES (?, ?, ?)
            ''', (user_id, req_id, pr_id))
            self.__db.commit()
            return True
        except Exception as e:
            return None

    def get_user_predictions(self, user_id):
        try:
            user_pr_data = self.__cur.execute('select * from user_predictions where user_id = ? ORDER BY id DESC', (user_id, )).fetchall()
            if user_pr_data:
                return [dict(item) for item in user_pr_data]
        except Exception as e:
            return None

    def get_user_data_from_id(self, user_id):
        try:
            user_id = int(user_id)
            user_data = self.__cur.execute('select * from users where id = ?', (user_id, )).fetchall()
            if user_data:
                return [dict(item) for item in user_data]
        except Exception as e:
            return None

    def delete_prediction(self, pr_id, user_id=None):
        try:
            if user_id:
                res = self.__cur.execute('select * from user_predictions where user_id = ? and prediction_id = ?', (user_id, pr_id)).fetchone()
                if not res:
                    return None

            prediction_id = int(pr_id)
            self.__cur.execute("DELETE FROM user_predictions WHERE prediction_id = ?", (prediction_id,))
            self.__db.commit()
            return True
        except Exception as e:
            return None

    def delete_prediction_from_list_id(self, list_id):
        ids = list_id['ids']
        placeholders = list_id['placeholders']
        try:
            self.__cur.execute(
                f"DELETE FROM user_predictions WHERE prediction_id IN ({placeholders})", ids)
            self.__db.commit()
            return self.__cur.rowcount
        except Exception as e:
            return None
