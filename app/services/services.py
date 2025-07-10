# app/services/services.py
import json

from flask import session, url_for
from flask_login import current_user
import pandas as pd

from ..controllers.real_estate_controller import Controller
from ..models.real_estate.models import RealEstateDB
from ..models.predicts.models import PredictDB
from ..ml.ml_service import process_model
from ..utils.utils import Utils
from logs.logclass import logger
from ..models.users.model import UserDB


def real_estate_data(req, db):
    """
    Handles requests for retrieving, filtering, and searching real estate data.

    Args:
        req: HTTP request with method and form parameters.
        db: Database connection.

    Returns:
        tuple: (results or error message, HTTP status code)
    """
    try:
        if not req:
            return {'error': 'Invalid input'}, 400

        re_data = []
        re_db = RealEstateDB(db)
        utils = Utils()

        re_data = utils.real_estate_data_filter()

        if req.method == 'POST':

            datatype = req.form.get('datatype')

            if not datatype:
                return {'error': 'Invalid input'}, 400

            if datatype == 'filter':
                filter_type = req.form.get('filter_value')
                filter_text = utils.process_filter_text(filter_type)
                if not filter_text:
                    return {'error': 'Invalid input filter value'}, 400

                re_data = re_db.get_all_data_filter(filter_text)

            elif datatype == 'search':
                search_value = req.form.get('search_value').lower()
                if not search_value:
                    return {'error': 'Invalid input search value'}, 400

                found_table_name, search_value_type = utils.filter_digit_data(search_value)
                if not search_value_type:
                    return {'error': 'No data found'}, 404

                if search_value_type.isdigit():
                    if found_table_name is None:
                        found_table_name, search_value_type = utils.filter_numbers_by_range(search_value_type)
                        if not search_value_type:
                            return {'error': 'No data found'}, 404
                    re_data = re_db.get_search_digit(found_table_name, search_value_type)

                else:
                    if found_table_name is None:
                        found_table_name, search_value_type = utils.search_text_filter(search_value_type)
                        if not search_value_type:
                            return {'error': 'No data found'}, 404
                    re_data = re_db.get_all_data_search(found_table_name, search_value_type)
            else:
                return {'error': 'Invalid data type'}, 400

        if not re_data:
            return {'error': 'No data found'}, 404

        return re_data, 200
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def predict_pr(req, db_re, db_pr, db_us):
    """
    Processes a POST request to predict real estate value based on input data.

    Args:
        req: HTTP request (expected to be POST with JSON or form data).
        db_re: Connection to the real estate data database.
        db_pr: Connection to the database for storing predictions.
        db_us: Connection to the user database.

    Returns:
        tuple: (prediction result or error message, HTTP status code)
    """
    try:

        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        json_data = req.get_json(silent=True)
        form_data = req.form

        input_data = None
        controller = Controller(req)

        re_con = RealEstateDB(db_re)
        min_data, max_data = re_con.get_min_max_data()

        if json_data:
            input_data = controller.filter_input_data_json(min_data, max_data)
        elif form_data:
            input_data = controller.filter_input_data_form(min_data, max_data)
        else:
            return {'error': 'Invalid input'}, 400

        if input_data is None:
            return {'error': 'Data processing error'}, 422

        if 'error_list' in input_data:
            return input_data, 422

        result = process_model(input_data, db_re)

        if result is None:
            return {'error': 'Data processing error'}, 422

        rec_pr = PredictDB(db_pr)

        last_id_req = rec_pr.save_request(input_data)
        last_id_pr = rec_pr.save_prediction(result, last_id_req)

        predict_list = session.get('predictions', [])
        predict_info = {
            'last_id_req': last_id_req,
            'last_id_pr': last_id_pr
        }
        predict_list.append(predict_info)

        session['predictions'] = predict_list

        if current_user.is_authenticated:
            user_db = UserDB(db_us)
            user_db.add_user_predictions(current_user.get_id(), last_id_req, last_id_pr)


        return result, 201

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def predictions_data(req, db):
    """
    Returns a list of predictions or search results based on them.

    Args:
        req: HTTP request with optional form parameters.
        db: Connection to the predictions database.

    Returns:
        tuple: (prediction data or error message, HTTP status code)
    """
    try:
        if not req:
            return {'error': 'Invalid input'}, 400

        pr_data = []
        pr_db = PredictDB(db)
        pr_data = pr_db.get_all_data()

        if req.method == 'POST':
            utils = Utils()

            datatype = req.form.get('datatype')
            if not datatype:
                return {'error': 'Invalid input'}, 400

            if datatype == 'search':
                search_data = req.form.get('search_value')
                search_data = json.loads(search_data)
                pr_data = pr_db.get_all_data_search(search_data)

            else:
                return {'error': 'Invalid data type'}, 400

        if not pr_data:
            return {'error': 'No data found'}, 404

        return pr_data, 200
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def statistics_data(db):
    """
    Generates statistics based on real estate data.

    Args:
        db: Connection to the real estate database.

    Returns:
        tuple: (dictionary with statistics or error message, HTTP status code)
    """
    try:
        utils = Utils()

        re_data = utils.real_estate_data_filter()

        if not re_data:
            return {'error': 'No data found'}, 404

        df = pd.DataFrame(re_data)

        top_expensive = df.nlargest(5, 'price')[
            ['id', 'price', 'district', 'rooms', 'floor', 'floors', 'area', 'type', 'cond', 'desc']].to_dict(orient='records')

        top_cheap = df.nsmallest(5, 'price')[
            ['id', 'price', 'district', 'rooms', 'floor', 'floors', 'area', 'type', 'cond', 'desc']].to_dict(orient='records')

        avg_price_district = df.groupby('district')['price'].mean().to_dict()

        type_distribution = df['type'].value_counts().to_dict()
        condition_distribution = df['cond'].value_counts().to_dict()
        rooms_distribution = df['rooms'].value_counts().to_dict()
        floors_distribution = df['floors'].value_counts().to_dict()
        floor_distribution = df['floor'].value_counts().to_dict()

        area_bins = pd.cut(df['area'], bins=[0, 30, 50, 70, 100, 150, 200, float('inf')])
        area_distribution = area_bins.value_counts(sort=False).astype(int).to_dict()
        area_distribution = {f"{interval.left}-{interval.right}": count for interval, count in area_distribution.items()}

        summary_stats = {
            'price': {
                'min': float(df['price'].min()),
                'max': float(df['price'].max()),
                'mean': float(df['price'].mean())
            },
            'area': {
                'min': float(df['area'].min()),
                'max': float(df['area'].max()),
                'mean': float(df['area'].mean())
            },
            'floor': {
                'min': int(df['floor'].min()),
                'max': int(df['floor'].max()),
                'mean': float(df['floor'].mean())
            },
            'floors': {
                'min': int(df['floors'].min()),
                'max': int(df['floors'].max()),
                'mean': float(df['floors'].mean())
            },
            'rooms': {
                'min': int(df['rooms'].min()),
                'max': int(df['rooms'].max()),
                'mean': float(df['rooms'].mean())
            }
        }

        statistics = {
            'top_expensive': top_expensive,
            'top_cheap': top_cheap,
            'avg_price_district': avg_price_district,
            'type_distribution': type_distribution,
            'condition_distribution': condition_distribution,
            'rooms_distribution': rooms_distribution,
            'floors_distribution': floors_distribution,
            'floor_distribution': floor_distribution,
            'area_distribution': area_distribution,
            'summary_stats': summary_stats
        }

        return statistics, 200

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))



def predict_user(req, db_pr, db_us):
    """
    Returns a list of user predictions (for an authenticated user or guest).

    Args:
        req: HTTP request (expected to be a GET method).
        db_pr: Connection to the predictions database.
        db_us: Connection to the user database.

    Returns:
        tuple: (list of predictions or error message, HTTP status code)
    """
    try:
        if req is None or req.method != 'GET':
            return {'error': 'Invalid input'}, 400

        data_list = []

        pr_db = PredictDB(db_pr)

        if current_user.is_authenticated:
            user_db = UserDB(db_us)
            req_pr_list = user_db.get_user_predictions(current_user.get_id())
            if not req_pr_list:
                return {'error': 'No data found'}, 404

            user_pr_list = []

            for item in req_pr_list:
                req_id = item['request_id']
                pr_id = item['prediction_id']

                user_pr_list.append(pr_db.get_predict_data(pr_id, req_id))

            data_list = user_pr_list
            data_list.append({'user': 'authenticated'})
        else:
            session_data = session.get('predictions', [])

            if not session_data:
                return {'error': 'No data found'}, 404

            last_request_id = [item['last_id_pr'] for item in session_data[::-1]]
            last_request_req = [item['last_id_req'] for item in session_data[::-1]]

            for i in range(len(last_request_id)):
                data_list.append(pr_db.get_predict_data(last_request_id[i], last_request_req[i]))

            data_list.append({'user': 'not authenticated'})
        if not data_list:
            return {'error': 'No data found'}, 404

        return data_list, 200
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def get_user_data(db):
    """
    Returns information about the current user, including name, email, type, and profile image.

    Args:
        db: Connection to the user database.

    Returns:
        tuple: (user data or error message, HTTP status code)
    """
    try:
        user_db = UserDB(db)

        user_data = user_db.get_user_data_from_id(current_user.get_id())

        user_type = 'admin' if current_user.is_admin() else 'user'
        user_image = url_for('static', filename=f'images/{user_type}_profile.png')

        user_data[0]['image'] = user_image

        if not user_data:
            return {'error': 'No data found'}, 404

        data = [{
            'name': user_data[0]['name'],
            'email': user_data[0]['email'],
            'image': user_data[0]['image'],
            'time': user_data[0]['time'],
            'type': user_type
        }]

        return data, 200
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def del_user_pr(req, db_us, db_pr):
    """
    Deletes a user prediction by its identifier.

    Args:
        req: HTTP request with JSON data containing 'request_id'.
        db_us: Connection to the user database.
        db_pr: Connection to the predictions database.

    Returns:
        tuple: (success or error message, HTTP status code)
    """
    try:
        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        data = req.get_json()
        if not data or 'request_id' not in data:
            return {'error': 'Invalid JSON data'}, 400

        predict_id = data['request_id']

        user_db = UserDB(db_us)
        prediction_db = PredictDB(db_pr)

        res_us = user_db.delete_prediction(predict_id, user_id=current_user.get_id())
        if not res_us:
            return {'error': 'Data processing error!'}, 404
        res_pr = prediction_db.delete_prediction(predict_id)
        if not res_pr:
            return {'error': 'Data processing error!'}, 404

        return {'success': True}, 200

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def delete_predictions(req, db_us, db_pr):
    """
    Deletes user predictions based on the specified mode and value. Admin access required.

    Args:
        req: HTTP request with form parameters 'delete_mode' and 'value'.
        db_us: Connection to the user database.
        db_pr: Connection to the predictions database.

    Returns:
        tuple: Success or error message and HTTP status code.
    """
    try:
        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        if not current_user.is_admin():
            return {'error': 'Access denied: insufficient permissions'}, 403

        delete_mode = req.form.get('delete_mode', None)
        value = req.form.get('value', None)

        try:
            count = int(value)
        except ValueError:
            return {'error': 'Invalid value type for deletion count'}, 400

        if not all([delete_mode, value]):
            return {'error': 'Invalid input data'}, 400

        user_db = UserDB(db_us)
        pred_db = PredictDB(db_pr)

        res = None

        if delete_mode == 'remove_id':
            res = user_db.delete_prediction(value)
            if not res:
                return {'error': 'Data processing error!'}, 422
            res = pred_db.delete_prediction(value)

        elif delete_mode in ['remove_top', 'remove_bottom']:
            direction = 'top' if delete_mode == 'remove_top' else 'bottom'

            list_id = pred_db.delete_data(count, direction)
            if not list_id:
                return {'error': 'Data processing error!'}, 422

            res = user_db.delete_prediction_from_list_id(list_id)

        else:
            return {'error': 'Invalid delete mode'}, 400

        if res is None:
            return {'error': 'No data found'}, 404

        return {'message': 'Deletion was successful!'}, 200

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))
