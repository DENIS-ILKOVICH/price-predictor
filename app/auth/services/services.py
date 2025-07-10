# app_sps/auth/services/services.py
from ..models.models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from ..src.user_login.user_login import UserLogin
from flask import session, current_app, make_response, url_for, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user
from datetime import *
from ..src.utils.utils import Utils
from logs.logclass import logger
import re


def auth_pr(db, form):
    """
    Authenticates a user based on login form data.

    Validates the form, searches for the user by email, compares the password,
    creates a user session, and sets a "remember me" token if needed.

    Args:
        db: Database connection object.
        form: Authentication form data (should include fields mail, psw, remember_me).

    Returns:
        tuple: A tuple (response, status_code) where response is a JSON response with
        the authentication result, and status_code is the HTTP status code
        (200 on success, 422 on validation or authentication errors).
    """
    try:
        userdb = Users(db)
        if not form.validate_on_submit():
            return {'success': False, 'message': "Input error", 'category': 'warning'}, 422

        user = userdb.get_user_by_email(form.mail.data)
        if not user:
            return {'success': False, 'message': "Invalid email or password", 'category': 'error'}, 422

        pass_db = user['password']
        pass_form = form.psw.data
        if not check_password_hash(pass_db, pass_form):
            return {'success': False, 'message': "Invalid email or password", 'category': 'error'}, 422

        user_login = UserLogin().create(user)
        if not user_login:
            return {'success': False, 'message': "Failed to create user session", 'category': 'error'}, 422

        login_user(user_login)
        session['user_id'] = current_user.get_id()

        response_data = {
            'success': True,
            'redirect': request.args.get("next") or url_for('predict.index')
        }

        response = make_response(jsonify(response_data), 200)

        if form.remember_me.data:
            token = userdb.generate_remember_token(current_app.secret_key, current_user.get_id())
            expires = datetime.utcnow() + timedelta(days=30)

            response.set_cookie(
                'remember_token',
                value=token,
                expires=expires,
                httponly=True,
                secure=True,
                samesite='Lax'
            )

        return response, 200

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))




def logout_pr(user_id, db):
    """
    Logs the user out of the system.

    If the user is authenticated, resets the "remember me" token in the database,
    deletes the token cookie, and ends the user session.

    Args:
        user_id (int or str): User identifier.
        db: Database connection object.

    Returns:
        tuple: A tuple (response, status_code) where response is a response object
        redirecting to the login page, and status_code is the HTTP status code (usually 200).
    """
    try:
        user = Users(db)

        if current_user.is_authenticated:
            user.remember_token_none(user_id)

        response = make_response(redirect(url_for('auth.login')))
        response.delete_cookie('remember_token')
        logout_user()

        return response, 200
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def register_pr(req,  db):
    """
    Handles registration of a new user.

    Validates input data, creates a user record in the database,
    hashes the password, authenticates the user, and creates a session.

    Args:
        req (flask.Request): HTTP request object containing registration form data.
        db: Database connection object.

    Returns:
        tuple or dict:
            - On successful registration: dictionary with keys 'success' and 'redirect' and HTTP status 201.
            - On validation error: dictionary with key 'error' and HTTP status 422.
            - On other errors: logs the error and returns None.
    """
    try:
        if not req:
            return {'error': 'Invalid input'}, 400

        user = Users(db)

        name = request.form.get('name', '').strip()
        email = request.form.get('mail', '').strip()
        psw = re.sub(r'\s+', '', request.form.get('psw', '').strip())
        psw2 = re.sub(r'\s+', '', request.form.get('psw2', '').strip())

        if not all([name, email, psw, psw2]):
            raise ValueError('Invalid data input')

        utils = Utils()
        result = utils.validate_registration(name, email, psw, psw2)
        if not result["success"]:
            return {'error': [result]}, 422

        hash_psw = generate_password_hash(psw)

        user_id = user.adduser(name, email, hash_psw)

        if not user_id:
            raise ValueError('Invalid data input')

        userlogin = UserLogin().create(user_id)
        login_user(userlogin)
        session['user_id'] = current_user.get_id()

        return {'success': True, 'redirect': request.args.get("next") or url_for('predict.index')}, 201

    except ValueError as e:
        return {'error': 'Invalid input', 'details': str(e)}, 422
    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def auto_login_pr(db_us):
    """
    Performs automatic user authentication via "remember me" token.

    Checks that the user is not authenticated in the current session,
    retrieves the token from cookies, validates it,
    and if the token is valid, logs the user in and creates a session.

    Args:
        db_us: User database connection object.

    Returns:
        tuple or dict:
            - On successful authentication: dictionary with status 'success' and HTTP status 200.
            - If the user is already authenticated: dictionary with status 'failed', message, and HTTP status 403.
            - If the token is missing or invalid: dictionary with status 'failed', error, and HTTP status 404 or 422.
    """
    try:

        userdb = Users(db_us)
        response = {}

        if current_user.is_authenticated:
            return {'status': 'failed', 'error': 'Already logged in'}, 403

        remember_token = request.cookies.get('remember_token')
        if not remember_token:
            return {'status': 'failed', 'error': 'No autosave data found'}, 404

        user = userdb.verify_remember_token(remember_token, current_app.secret_key)
        if not user:
            return {'status': 'failed', 'error': 'Incorrect autosave data'}, 422

        userlogin = UserLogin().create(user)

        session['user_type'] = 'user'
        login_user(userlogin)
        session['user_id'] = current_user.get_id()

        return {'status': 'success', 'message': 'Successful authorization'}, 200


    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))


def change_email_pr(req, db_us):
    """
    Handles the process of changing a user's email with two-factor verification.

    The process involves several steps:
    1. Generating and sending a verification code to the user's current email.
    2. Verifying the confirmation code entered by the user.
    3. Checking the user's password.
    4. Validating and updating the new email if it is valid and not already taken.

    Args:
        req: Request object containing data for the email change.
        db_us: User database connection object.

    Returns:
        JSON response with the result and HTTP status code.
    """
    try:
        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        data = req.get_json()
        if not data:
            return {'error': 'Empty JSON body'}, 400

        action = data.get('action', '').strip()
        if not action:
            return {'error': 'Invalid input action'}, 400

        import random

        code = session.get('code', '')
        if not code:
            code = str(random.randint(100000, 999999))
            session['code'] = code

            utils = Utils()
            res = utils.send_email_message(current_user.get_email(), code)
            if not res:
                return {'error': 'Data processing error'}, 422
            return {'message': 'Code created'}, 201

        if code:
            if not session.get('code_verify'):
                code_verify = data.get('code', '').strip()
                if not code_verify:
                    return {'error': 'Invalid input code verify'}, 400

                if code_verify == code:
                    session['code_verify'] = True
                    return {'message': 'Code verified'}, 200
                return {'error': 'Invalid code value'}, 422

            password = data.get('password', '').strip()

            if not check_password_hash(current_user.get_password(), password):
                return {'error': 'Wrong password'}, 403

            new_email = data.get('email', '').strip()
            if not new_email:
                return {'error': 'Missing email'}, 400

            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

            if not re.match(email_pattern, new_email):
                return {'error': 'Invalid email format'}, 400

            user_db = Users(db_us)
            if user_db.get_user_by_email(new_email):
                return {'error': 'Email already in use'}, 409

            res = user_db.change_email(current_user.get_id(), new_email)
            if not res:
                return {'error': 'Data processing error'}, 422

        session.pop('code', None)
        session.pop('code_verify', None)
        return {'message': 'Email successfully changed'}, 201

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))
        return {'error': 'Internal server error'}, 500



def change_password_pr(req, db_us):
    """
    Handles a user password change request with validation of the old password and the new one.

    Args:
        req: HTTP request containing JSON data (old password, new password, and new password confirmation).
        db_us: User database.

    Returns:
        JSON response with the operation result and HTTP status code.
    """
    try:
        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        data = req.get_json()
        if not data:
            return {'error': 'Empty JSON body'}, 400

        old_password = re.sub(r'\s+', '', data.get('old_password', ''))
        new_password = re.sub(r'\s+', '', data.get('new_password', ''))
        new_password_repeat = re.sub(r'\s+', '', data.get('new_password_repeat', ''))

        if not old_password:
            return {'error': 'Old password is required'}, 400

        if not new_password:
            return {'error': 'New password is required'}, 400

        if not new_password_repeat:
            return {'error': 'Repeat password is required'}, 400

        if not check_password_hash(current_user.get_password(), old_password):
            return {'error': 'Wrong password'}, 403

        utils = Utils()
        val_pasw = utils.validate_password(new_password, new_password_repeat)

        if not val_pasw['success']:
            return {'error': val_pasw['message']}, 422

        hash_psw = generate_password_hash(new_password)

        user_db = Users(db_us)
        res = user_db.change_passw(current_user.get_id(), hash_psw)

        if not res:
            return {'error': 'Data processing error'}, 422

        return {'message': 'Password successfully changed'}, 201

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))
        return {'error': 'Internal server error'}, 500


def change_name_pr(req, db_us):
    """
    Handles a user name change request with validation of the new name.

    Args:
        req: HTTP request containing JSON data (new user name).
        db_us: User database.

    Returns:
        JSON response with the operation result and HTTP status code.
    """
    try:
        if req is None or req.method != 'POST':
            return {'error': 'Invalid input data'}, 400

        data = req.get_json()
        if not data:
            return {'error': 'Empty JSON body'}, 400

        new_name = data.get('username', '')

        if not new_name:
            return {'error': 'Username is required'}, 400

        utils = Utils()
        val_name = utils.validate_name(new_name)
        if not val_name['success']:
            return {'error': val_name['message']}, 422

        user_db = Users(db_us)
        res = user_db.change_name(current_user.get_id(), new_name)

        if not res:
            return {'error': 'Data processing error'}, 422

        return {'message': 'Username successfully changed'}, 201

    except Exception as e:
        logger.log_error("Internal server error in services", stack_trace=str(e))
        return {'error': 'Internal server error'}, 500

