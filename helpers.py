from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, request
from models.imports import Environment

print("Helpers imported")

def helpers_test():
    print("Helpers call test")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



