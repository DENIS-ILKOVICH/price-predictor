# app/models/predict/models.py
import datetime

class PredictDB:
    def __init__(self, db):
        if db is None:
            raise ValueError("Database connection is not established.")
        self.__db = db
        self.__cur = db.cursor()


    def save_request(self, data):
        try:
            data.pop('desc', None)
            district, rooms, floor, floors, area, datatype, cond, walls = data.values()
            timestamp = datetime.datetime.now()

            last_id = self.__cur.execute('SELECT id FROM requests ORDER BY id DESC LIMIT 1').fetchone()
            if not last_id:
                last_id = 1

            last_id = int(last_id[0]) + 1

            self.__cur.execute('''
                INSERT INTO requests (id, district, rooms, floor, floors, area, type, cond, walls, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (last_id, district, rooms, floor, floors, area, datatype, cond, walls, timestamp))
            self.__db.commit()
            return last_id
        except Exception as e:
            return None


    def save_prediction(self, data, req_id):
        try:
            price = data['predicted_price']
            mean_error, mse = 9521.48 , 59999999
            timestamp = datetime.datetime.now()

            last_id = self.__cur.execute('SELECT id FROM predictions ORDER BY id DESC LIMIT 1').fetchone()
            if not last_id:
                last_id = 1

            last_id = int(last_id[0]) + 1
            self.__cur.execute('''
                INSERT INTO predictions (id, price, mean_error, mse, request_id, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (last_id, price, mean_error, mse, req_id, timestamp))
            self.__db.commit()
            return last_id
        except Exception as e:
            print(e)
            return None

    def get_all_data(self):
        try:
            query = '''
                SELECT p.*, r.district, r.rooms, r.floor, r.floors, r.area, 
                       r.type, r.cond, r.walls, r.timestamp AS request_timestamp
                FROM predictions p
                JOIN requests r ON p.request_id = r.id
                ORDER BY r.id DESC
            '''
            data = self.__cur.execute(query).fetchall()
            if data:
                return [dict(item) for item in data]
            return None
        except Exception as e:
            return None

    def get_predict_data(self, predict_id, request_id):
        try:
            query = '''
                SELECT p.*, r.district, r.rooms, r.floor, r.floors, r.area, 
                       r.type, r.cond, r.walls, r.timestamp AS request_timestamp
                FROM predictions p
                JOIN requests r ON p.request_id = r.id
                WHERE p.id = ? AND r.id = ?
                ORDER BY r.id DESC
            '''
            data = self.__cur.execute(query, (predict_id, request_id)).fetchall()
            if data:
                return [dict(item) for item in data]
            return None
        except Exception as e:
            return None

    def get_all_data_search(self, search_data):
        try:
            query = '''
                SELECT p.*, r.district, r.rooms, r.floor, r.floors, r.area, 
                       r.type, r.cond, r.walls, r.timestamp AS request_timestamp
                FROM predictions p
                JOIN requests r ON p.request_id = r.id
            '''
            params = ()
            where_clauses = []


            if 'price' in search_data and search_data['price']:
                if search_data['price'].isdigit():
                    price = int(search_data['price'])
                    where_clauses.append('p.price BETWEEN ? AND ?')
                    params += (price - 5000, price + 5000)
                else:
                    return None

            elif 'request_id' in search_data and search_data['request_id']:
                if search_data['request_id'].isdigit():
                    where_clauses.append('p.request_id = ?')
                    params += (int(search_data['request_id']),)
                else:
                    return None

            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)

            query += ' ORDER BY r.id DESC'

            data = self.__cur.execute(query, params).fetchall()

            if data:
                return [dict(item) for item in data]
            return None

        except Exception as e:
            return None

    def delete_data(self, param, dtype):
        try:
            num_delete = int(param)

            if dtype == 'top':
                self.__cur.execute(
                    "SELECT id FROM predictions LIMIT ?", (num_delete,))
            elif dtype == 'bottom':
                self.__cur.execute(
                    "SELECT id FROM predictions ORDER BY id DESC LIMIT ?", (num_delete,))
            else:
                return None

            ids_to_delete = self.__cur.fetchall()

            if not ids_to_delete:
                return None

            ids = [row[0] for row in ids_to_delete]
            placeholders = ','.join('?' for _ in ids)

            self.__cur.execute(
                f"DELETE FROM requests WHERE id IN ({placeholders})", ids)

            self.__cur.execute(
                f"DELETE FROM predictions WHERE request_id IN ({placeholders})", ids)

            self.__db.commit()

            return {
                'placeholders':placeholders,
                'ids':ids
            }
        except Exception as e:
            return None

    def delete_prediction(self, pr_id):
        try:
            prediction_id = int(pr_id)
            pr = self.__cur.execute('select * from predictions where id = ?', (prediction_id, )).fetchone()
            rq = self.__cur.execute('select * from predictions where id = ?', (prediction_id, )).fetchone()
            if not all([pr, rq]):
                return None

            self.__cur.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
            self.__cur.execute("DELETE FROM requests WHERE id = ?", (prediction_id,))
            self.__db.commit()
            return True
        except Exception as e:
            return None


