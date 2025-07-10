# app/auth/routes.py
from flask import *
from flask_login import *
from .src.login_form.login_form import LoginForm
from ..database.dbconnection import db_instance
from .services.services import  *
from logs.logclass import logger
from werkzeug.exceptions import HTTPException

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    try:
        db = db_instance.get_db('users')
        db_us = Users(db)
        user_id = session.get('user_id')

        return UserLogin().fromDB(user_id, db_us)
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise

@auth.route('/login', methods=['POST', 'GET'])
def login():
    try:
        logger.log_request(request)

        if current_user.is_authenticated:
            return redirect('/')

        db_us = db_instance.get_db('users')

        form = LoginForm()
        if request.method == 'POST':
            response, status_code = auth_pr(db_us, form)

            if status_code == 422:
                return jsonify(response)
            return response

        return render_template('login.html', title='Login', style_href='css/login.css', form=form)

    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@auth.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    try:
        logger.log_request(request)

        db_us = db_instance.get_db('users')
        response, status_code = logout_pr(current_user.get_id(), db_us)
        logout_status = response if status_code == 200 else None

        return logout_status
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@auth.route('/register', methods=['POST', 'GET'])
def register():
    try:
        logger.log_request(request)
        db_us = db_instance.get_db('users')

        if request.method == 'POST':
            response, status_code = register_pr(request, db_us)
            if status_code == 422:
                return jsonify(response)
            return response

        return render_template('register.html', title='Sign Up', style_href='css/register.css')
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))
    raise


@auth.route('/auto_login', methods=['POST', 'GET'])
def auto_login():
    try:
        logger.log_request(request)

        db_us = db_instance.get_db('users')
        response, status_code = auto_login_pr(db_us)

        return response
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@auth.route('/check_auth', methods=['GET'])
def check_auth():
    try:
        status = 'unauthorized'
        user_info = {}
        if current_user.is_authenticated:
            status = 'authorized'
            user_type = 'admin' if current_user.is_admin() else 'user'
            user_image = url_for('static', filename=f'images/{user_type}_profile.png')

            user_info = {
                'name': current_user.get_name(),
                'avatar': user_image
            }
        return jsonify({'status': status, 'user': user_info})
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))



@auth.route('/change_email', methods=['POST'])
@login_required
def change_email():
    try:
        db_us = db_instance.get_db('users')
        response, status_code = change_email_pr(request, db_us)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        db_us = db_instance.get_db('users')
        response, status_code = change_password_pr(request, db_us)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))


@auth.route('/change_username', methods=['POST'])
@login_required
def change_name():
    try:
        db_us = db_instance.get_db('users')
        response, status_code = change_name_pr(request, db_us)

        return jsonify(response), status_code
    except Exception as e:
        logger.log_error("Internal Server Error", stack_trace=str(e))

@auth.errorhandler(Exception)
def handle_exception(e):
    code = 500
    description = "Internal Server Error"
    if isinstance(e, HTTPException):
        logger.log_error("Internal Server Error", stack_trace=f'{e.description}, {e.code}')


    return render_template("error.html", title='Error', code=code, description=description, style_href='css/error.css'), code

