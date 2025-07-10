# app/models/real_estate/models.py
class RealEstateDB:
    def __init__(self, db):
        if db is None:
            raise ValueError("Database connection is not established.")
        self.__db = db
        self.__cur = db.cursor()

    def get_all_data(self):
        try:
            data = self.__cur.execute('select * from real_estate').fetchall()
            if data:
                return [dict(item) for item in data]
        except Exception as e:
            return None

    def get_all_data_filter(self, filter):
        try:
            data = self.__cur.execute(f'select id, {filter} from real_estate').fetchall()
            if data:
                return [dict(item) for item in data]
        except Exception as e:
            return None


    def get_all_data_search(self, table_name, search_text):
        try:
            search_text = f"%{search_text}%"
            data = self.__cur.execute(f'select * from real_estate where {table_name} LIKE ?', (search_text, )).fetchall()

            if data:
                return [dict(item) for item in data]
        except Exception as e:
            return None


    def get_search_digit(self, table_name, search_num):
        try:
            search_value = int(search_num)
            table_name = str(table_name)
            data = self.__cur.execute(f'select * from real_estate where {table_name} = ?', (search_value, )).fetchall()

            if data:
                return [dict(item) for item in data]
        except Exception as e:
            return None

    def get_min_max_data(self):
        try:

            min_result = self.__cur.execute("SELECT MIN(rooms), MIN(floor), MIN(floors), MIN(area) FROM real_estate").fetchone()
            max_result = self.__cur.execute("SELECT MAX(rooms), MAX(floor), MAX(floors), MAX(area) FROM real_estate").fetchone()

            if min_result and max_result:
                min_data = {
                    'min_rooms': min_result[0],
                    'min_floor': min_result[1],
                    'min_floors': min_result[2],
                    'min_area': min_result[3],
                }

                max_data = {
                    'max_rooms': max_result[0],
                    'max_floor': max_result[1],
                    'max_floors': max_result[2],
                    'max_area': max_result[3],
                }

                return min_data, max_data

        except Exception as e:
            return None

    def get_data_from_id(self, num_id):
        try:
            search_value = int(num_id)
            data = self.__cur.execute(f'select * from real_estate where id = ?', (search_value, )).fetchall()

            if data:
                return [dict(item) for item in data]
        except Exception as e:
            return None
