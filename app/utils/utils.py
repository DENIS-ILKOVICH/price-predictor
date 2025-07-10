# app/utils/utils.py
from app.use_cases.data_processing_use_case import extract_features
from app.config import Config
import sqlite3
import pandas as pd
import numpy as np
import re

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def search_text_filter(text, found_table_name=None):
        try:

            district = ['primorsky', 'malinovsky', 'kievsky', 'suvorovsky']

            types_of_houses = ["new", "new ", "czech", "special project", "khrushchevka", "guest", "old fund",
                               "kharkiv",
                               "moscow", "cellular", "belgian", "stalinka", "jugoslavsky", "a small family",
                               "private house", "under construction", "house under construction"]

            cond = ["renovation", "after builders", "after overhaul", "after makeup", "residential clean",
                    "need. in cap. renovation", "need. in cosm. renovation", "need. in tech. renovation",
                    "author's design", "modern design", "expanded clay-concrete", "building materials",
                    "design classic", "house under construction"]

            walls = ["brick", "monolith", "panel", "block-brick", "shell rock", "aerated concrete",
                     "foam concrete", "reed, dranka", "blocky", "plastic", "mixed", "concrete",
                     "reinforced concrete", "shell brick", "metal-plastic", "metalwork", "wood",
                     "silicate brick"]

            found_value = None

            for list_name, list_data in [('district', district), ('type', types_of_houses),
                                         ('cond', cond), ('walls', walls)]:
                for item in list_data:
                    if text in item:
                        found_value = item
                        if found_table_name is None:
                            found_table_name = list_name
                        break
                if found_value:
                    break

            if found_value:
                return found_table_name, found_value

            return None, None
        except Exception as e:
            return None, None



    @staticmethod
    def process_filter_text(text):
        try:
            if not text:
                return None

            allowed_columns = ['price', 'district', 'rooms', 'floor', 'floors', 'area', 'type', 'cond', 'walls', 'desc']
            if text in allowed_columns:
                return text
        except Exception as e:
            return None

    @staticmethod
    def filter_numbers_by_range(value):
        try:
            if 0 < int(value) < 4:
                found_table_name = 'rooms'
            elif 3 < int(value) < 10:
                found_table_name = 'floor'
            elif 9 < int(value) < 26:
                found_table_name = 'floors'
            elif 25 < int(value) < 200:
                found_table_name = 'area'
            else:
                found_table_name = 'price'

            if found_table_name:
                return found_table_name, value
        except Exception as e:
            return None

    import re

    @staticmethod
    def validate_input_data_from_model(data, min_data, max_data):
        try:
            district = data.get('district', '')
            rooms = data.get('rooms', 0)
            floor = data.get('floor', 0)
            floors = data.get('floors', 0)
            area = data.get('area', 0)
            type_data = data.get('type', '')
            cond = data.get('cond', '')
            walls = data.get('walls', '')
            desc = data.get('desc', '')

            min_rooms = min_data.get('min_rooms', 0)
            min_floor = min_data.get('min_floor', 0)
            min_floors = min_data.get('min_floors', 0)
            min_area = min_data.get('min_area', 0)

            max_rooms = max_data.get('max_rooms', 0)
            max_floor = max_data.get('max_floor', 0)
            max_floors = max_data.get('max_floors', 0)
            max_area = max_data.get('max_area', 0)

            error_list = []

            if not district or district.lower() not in [
                'primorsky', 'malinovsky', 'kievsky', 'suvorovsky']:
                error_list.append({'error': 'Invalid value for field: district'})

            if not type_data or type_data.lower() not in [
                "new", "czech", "special project", "khrushchevka", "guest", "old fund", "kharkiv",
                "moscow", "cellular", "belgian", "stalinka", "jugoslavsky", "a small family",
                "private house", "under construction"]:
                error_list.append({'error': 'Invalid value for field: type'})

            if not cond or cond.lower() not in [
                "renovation", "after builders", "after overhaul", "after makeup", "residential clean",
                "need. in cap. renovation", "need. in cosm. renovation", "need. in tech. renovation",
                "author's design", "modern design", "expanded clay-concrete"]:
                error_list.append({'error': 'Invalid value for field: cond'})

            if not walls or walls.lower() not in [
                "brick", "monolith", "panel", "block-brick", "shell rock", "aerated concrete",
                "foam concrete", "reed, dranka"]:
                error_list.append({'error': 'Invalid value for field: walls'})

            if rooms < min_rooms or rooms > max_rooms:
                error_list.append({'error': 'Invalid value for field: rooms'})

            if floor < min_floor or floor > max_floor:
                error_list.append({'error': 'Invalid value for field: floor'})

            if floors < min_floors or floors > max_floors:
                error_list.append({'error': 'Invalid value for field: floors'})

            if floors < floor:
                error_list.append({'error': 'Invalid value: total floors cannot be less than current floor'})

            if area < min_area + 10 or area > max_area:
                error_list.append({'error': 'Invalid value for field: area'})

            if desc:
                suspicious_patterns = [
                    r'<\s*script.*?>',
                    r'eval\s*\(',
                    r'alert\s*\(',
                    r'onerror\s*=',
                    r'onload\s*=',
                    r'\{.*?\}',
                    r'<[a-zA-Z]+\s*>',
                    r'(SELECT|DROP|INSERT|DELETE|UPDATE|ALTER|CREATE|EXEC|UNION|OR\s+1=1)',
                    r'--',
                    r';',
                    r'/\*.*?\*/',
                ]

                pattern = re.compile('|'.join(suspicious_patterns), re.IGNORECASE | re.DOTALL)
                latin_only_pattern = re.compile(r'^[a-zA-Z0-9\s.,!?+()\-\"\'%]+$')



                if pattern.search(desc) and not re.search(r'"[A-Za-z\s]+"', desc):
                    error_list.append({'error': 'Illegal characters or suspicious code detected!'})

                if not latin_only_pattern.fullmatch(desc):
                    error_list.append(
                        {'error': 'Description must contain only English (Latin) letters and allowed symbols!'})

            if error_list:
                return error_list

            return None

        except Exception as e:
            return None

    def filter_digit_data(self, data):
        try:
            if not data:
                return None

            table_list = ["id", "price", "district", "rooms", "floor", "floors", "area", "type", "cond", "walls"]
            search_data = data.lower().strip()

            if ':' not in data:
                return None, data

            import re
            cleaned_data = re.sub(r'\s*:\s*', ':', search_data)
            data_list = cleaned_data.split(":")

            if data_list and len(data_list) == 2:
                if data_list[0] in table_list:
                    if data_list[1].isdigit():
                        return data_list[0], data_list[1]
                    else:
                        found_table_name, found_value = self.search_text_filter(data_list[1], found_table_name=data_list[0])
                        return found_table_name, found_value
            return None, None

        except Exception as e:
            return None

    @staticmethod
    def filter_data():
        """
        Load data from SQLite database, clean and preprocess it for model training.
        Extract features from descriptions and remove invalid, duplicate, and outlier records.
        Return cleaned DataFrame.
        """

        query = "SELECT price, district, rooms, floor, floors, area, type, cond, walls, desc FROM real_estate"
        conn = sqlite3.connect(Config.DATABASE_REAL_ESTATE)
        df = pd.read_sql(query, conn)

        critical_columns = ['area', 'rooms', 'floor', 'floors', 'type', 'cond', 'walls']

        if 'desc' in df.columns and not pd.isna(df['desc']).iloc[0]:
            features = df['desc'].apply(extract_features)
            df['property_level'] = features.apply(lambda x: x['property_level'])
            if 'warning' in features.iloc[0]:
                df['warning'] = features.apply(lambda x: x.get('warning', None))
            df = df.drop(columns=['desc'])
        else:
            df['property_level'] = 5
            df['warning'] = 'Description (desc) missing, lowest quality level assigned (5)'

        df[critical_columns] = df[critical_columns].replace(['', ' ', 'None'], np.nan)
        df.dropna(subset=critical_columns, how='any', inplace=True)

        df.drop_duplicates(inplace=True)

        df = df[(df['price'] >= 10000)]
        df = df[df['area'].between(10, 300)]
        df = df[df['rooms'].between(1, 10)]
        df = df[df['floor'] <= df['floors']]

        price_upper = df['price'].quantile(0.995)
        df = df[df['price'] <= price_upper]

        categorical_columns = ['district', 'type', 'cond', 'walls']
        from collections import defaultdict
        value_counts_by_column = defaultdict(lambda: defaultdict(int))

        for col in categorical_columns:
            for value, count in df[col].value_counts().items():
                value_counts_by_column[value][col] = count

        rows_to_drop = set()
        for value, columns_dict in value_counts_by_column.items():
            if len(columns_dict) <= 1:
                continue
            correct_column = max(columns_dict, key=columns_dict.get)
            for wrong_column in columns_dict:
                if wrong_column != correct_column:
                    bad_rows = df[df[wrong_column] == value].index
                    rows_to_drop.update(bad_rows)

        df.drop(index=rows_to_drop, inplace=True)

        df['price_per_sqm'] = df['price'] / df['area']
        lower_bound = df['price_per_sqm'].quantile(0.025)
        upper_bound = df['price_per_sqm'].quantile(0.995)
        df = df[(df['price_per_sqm'] >= lower_bound) & (df['price_per_sqm'] <= upper_bound)]
        df.drop(columns=['price_per_sqm'], inplace=True)

        return df

    @staticmethod
    def real_estate_data_filter():
        """
        Load data from SQLite database, clean and preprocess it for model training.
        Extract features from descriptions and remove invalid, duplicate, and outlier records.
        Return cleaned DataFrame and count of records with price > 150000.
        """

        query = "SELECT * FROM real_estate"
        conn = sqlite3.connect(Config.DATABASE_REAL_ESTATE)
        df = pd.read_sql(query, conn)

        critical_columns = ['area', 'rooms', 'floor', 'floors', 'type', 'cond', 'walls']

        df[critical_columns] = df[critical_columns].replace(['', ' ', 'None'], np.nan)
        df.dropna(subset=critical_columns, how='any', inplace=True)

        df.drop_duplicates(inplace=True)

        df = df[(df['price'] >= 10000)]
        df = df[df['area'].between(10, 300)]
        df = df[df['rooms'].between(1, 10)]
        df = df[df['floor'] <= df['floors']]

        price_upper = df['price'].quantile(0.995)
        df = df[df['price'] <= price_upper]

        categorical_columns = ['district', 'type', 'cond', 'walls']
        from collections import defaultdict
        value_counts_by_column = defaultdict(lambda: defaultdict(int))

        for col in categorical_columns:
            for value, count in df[col].value_counts().items():
                value_counts_by_column[value][col] = count

        rows_to_drop = set()
        for value, columns_dict in value_counts_by_column.items():
            if len(columns_dict) <= 1:
                continue
            correct_column = max(columns_dict, key=columns_dict.get)
            for wrong_column in columns_dict:
                if wrong_column != correct_column:
                    bad_rows = df[df[wrong_column] == value].index
                    rows_to_drop.update(bad_rows)

        df.drop(index=rows_to_drop, inplace=True)

        df['price_per_sqm'] = df['price'] / df['area']
        lower_bound = df['price_per_sqm'].quantile(0.025)
        upper_bound = df['price_per_sqm'].quantile(0.995)
        df = df[(df['price_per_sqm'] >= lower_bound) & (df['price_per_sqm'] <= upper_bound)]
        df.drop(columns=['price_per_sqm'], inplace=True)

        count_price_above_150k = df[df['price'] > 150000].shape[0]


        return df.to_dict(orient='records')
