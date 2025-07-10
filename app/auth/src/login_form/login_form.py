#app/auth/src/login_form/login_form.py
from flask_wtf import *
from wtforms import *
from wtforms.validators import *

class LoginForm(FlaskForm):
    mail = StringField(validators=[Email()])
    psw = PasswordField(validators=[DataRequired(), Length(min=4, max=35)])
    remember_me = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = ['Email', 'Password', 'Remember me', 'Sign In']

        self.mail.label.text = f"{labels[0]}: "
        self.psw.label.text = f"{labels[1]}: "
        self.remember_me.label.text = f"{labels[2]}"
        self.submit.label.text = f"{labels[3]}"

