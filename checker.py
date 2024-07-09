from flask import session
from functools import wraps

def check_logged_in (func):
    @wraps(func)
    def wrapper(*args, **kwrgs):
        if 'logged_in' in session:
            return func(*args, **kwrgs)
        return 'You need to login to access this page.'
    return wrapper