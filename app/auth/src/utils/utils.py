#app/auth/src/utils/utils.py
import re
from flask import render_template, current_app
from flask_mail import Message

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def validate_registration(name, mail, psw, psw2):

        if not all([name.strip(), mail.strip(), psw.strip(), psw2.strip()]):
            return {'success': False, 'message': "Усі поля є обов’язковими для заповнення.", 'category': 'warning'}

        if len(name) < 2:
            return {'success': False, 'message': "Ім’я має містити щонайменше 2 символи.", 'category': 'warning'}

        if len(name) > 15:
            return {'success': False, 'message': "Ім’я має містити не більше 15 символів.", 'category': 'warning'}

        if not re.fullmatch(r"[a-zA-Zа-яА-ЯіїєІЇЄ0-9_]+", name):
            return {'success': False, 'message': "Ім’я може містити лише літери, цифри або знак підкреслення '_'.",
                    'category': 'warning'}

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, mail):
            return {'success': False, 'message': "Некоректний email.", 'category': 'warning'}

        if len(psw) < 6:
            return {'success': False, 'message': "Пароль має містити щонайменше 6 символів.", 'category': 'warning'}

        if not re.search(r'[A-Za-z]', psw) or not re.search(r'\d', psw):
            return {'success': False, 'message': "Пароль має містити літери й цифри.", 'category': 'warning'}

        if psw != psw2:
            return {'success': False, 'message': "Паролі не співпадають.", 'category': 'warning'}

        return {"success": True}

    @staticmethod
    def send_email_message(to_email, code):
        try:

            html = render_template("change_data.html", message='пошти', code=code)
            mail = current_app.extensions['mail']
            msg = Message(
                subject="Email change confirmation",
                recipients=[to_email],
                html=html,
            )
            mail.send(msg)

            return True
        except Exception as e:
            return None


    @staticmethod
    def validate_password(psw1, psw2):
        """
        Validates the password strength and match.

        Rules:
        - Must be at least 6 characters long
        - Must include both letters and numbers
        - Must match the confirmation password

        Args:
            psw1 (str): The password entered by the user.
            psw2 (str): The password confirmation.

        Returns:
            dict or None: Validation result with success flag and message.
        """
        try:
            if len(psw1) < 6:
                return {'success': False, 'message': "The password must contain at least 6 characters."}

            if not re.search(r'[A-Za-z]', psw1) or not re.search(r'\d', psw1):
                return {'success': False, 'message': "The password must contain both letters and numbers."}

            if psw1 != psw2:
                return {'success': False, 'message': "Passwords do not match."}

            return {"success": True}
        except Exception:
            return None

    @staticmethod
    def validate_name(name):
        try:
            if len(name) < 2:
                return {'success': False, 'message': "The name must contain at least 2 characters."}

            if len(name) > 15:
                return {'success': False, 'message': "The name must contain no more than 15 characters."}

            if not re.fullmatch(r"[a-zA-Zа-яА-ЯіїєІЇЄ0-9_]+", name):
                return {'success': False, 'message': "The name may contain only letters, numbers, or the underscore '_' character."}

            return {"success": True}
        except Exception:
            return None