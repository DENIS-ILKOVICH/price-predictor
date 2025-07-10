# run.py
from app import create_app
from flask import session
from app.auth.routes import auto_login

app = create_app()

@app.before_request
def before_request():
    if "first_request_done" not in session:
        session["first_request_done"] = True
        auto_login()

if __name__ == '__main__':
    app.run(debug=True)


