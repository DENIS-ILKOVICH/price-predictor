# app/route.py
from flask import *
from flask_login import login_required, current_user
from .services.services import predict_pr, real_estate_data, predictions_data, statistics_data, predict_user, \
     get_user_data, del_user_pr, delete_predictions
from logs.logclass import logger
from werkzeug.exceptions import HTTPException
import json

predict = Blueprint('predict', __name__)

from .database import database


@predict.route('/')
def index():
    try:
        logger.log_request(request)

        with open('app/ml/metrics_results.json', 'r') as f:
            metrics = json.load(f)

        return render_template('main.html', title='Home', metrics=metrics, style_href='css/main.css',
                               js_href1='js/main/main.js', js_href2='js/main/faq.js')
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@predict.route('/predict', methods=['POST', 'GET'])
def predict_():
    try:
        logger.log_request(request)

        with open('app/ml/metrics_results.json', 'r') as f:
            metrics = json.load(f)

        return render_template('predict.html', title='Predict',
                               style_href='css/predict.css', metrics=metrics, js_href1='js/predict/predict_form.js',
                               js_href2='js/predict/predict_history.js')
    except Exception as e:
        logger.log_error("Data processing error", stack_trace=str(e))
    raise


@predict.route('/get_predict', methods=['POST'])
def get_predict():
    try:
        logger.log_request(request)

        db_re = g.get_db('real_estate')
        db_pr = g.get_db('predictions')
        db_us = g.get_db('users')
        response, status_code = predict_pr(request, db_re, db_pr, db_us)
        import time
        time.sleep(3.35)
        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/user_predictions', methods=['GET'])
def user_predictions():
    try:
        logger.log_request(request)

        db_pr = g.get_db('predictions')
        db_us = g.get_db('users')
        response, status_code = predict_user(request, db_pr, db_us)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/profile')
@login_required
def profile():
    try:
        logger.log_request(request)

        return render_template('profile.html', title='Profile',
                               style_href='css/profile.css', js_href1='js/profile/profile.js', js_href2='js/profile/change_data.js', js_href3='js/animations/profile_gear.js')

    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@predict.route('/dataframe', methods=['POST', 'GET'])
def dataframe():
    try:
        logger.log_request(request)

        return render_template('dataframe.html', style_href='css/dataframe.css', title='DataFrame',
                               js_href='js/dataframe/dataframe.js')
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@predict.route('/sort_dataframe', methods=['POST', 'GET'])
def sort_dataframe():
    try:
        logger.log_request(request)

        db = g.get_db('real_estate')
        response, status_code = real_estate_data(request, db)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/predictions', methods=['POST', 'GET'])
def predictions():
    try:
        logger.log_request(request)

        return render_template('predictions.html', title='Predictions', style_href='css/predictions.css',
                               js_href='js/predictions/predictions.js')
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@predict.route('/sort_predictions', methods=['POST', 'GET'])
def sort_predictions():
    try:
        logger.log_request(request)

        db = g.get_db('predictions')
        response, status_code = predictions_data(request, db)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/statistics', methods=['POST', 'GET'])
def statistics():
    try:
        logger.log_request(request)

        return render_template('statistics.html', title='Statistics', style_href='css/statistic.css',
                               js_href='js/statistics/statistics.js')
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@predict.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        logger.log_request(request)

        db = g.get_db('real_estate')
        response, status_code = statistics_data(db)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))



@predict.route('/get_user', methods=['POST', 'GET'])
@login_required
def get_user():
    try:
        logger.log_request(request)

        db_us = g.get_db('users')
        response, status_code = get_user_data(db_us)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/del_user_prediction', methods=['POST', 'GET'])
@login_required
def del_user_prediction():
    try:
        logger.log_request(request)

        db_us = g.get_db('users')
        db_pr = g.get_db('predictions')
        response, status_code = del_user_pr(request, db_us, db_pr)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.route('/del_predictions', methods=['POST', 'GET'])
@login_required
def del_predictions():
    try:
        logger.log_request(request)

        db_us = g.get_db('users')
        db_pr = g.get_db('predictions')
        response, status_code = delete_predictions(request, db_us, db_pr)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@predict.errorhandler(Exception)
def handle_exception(e):
    code = 500
    description = "Internal Server Error"
    if isinstance(e, HTTPException):
        logger.log_error("Internal Server Error", stack_trace=f'{e.description}, {e.code}')

    return render_template("error.html", title='Error', code=code, description=description,
                           style_href='css/error.css'), code


