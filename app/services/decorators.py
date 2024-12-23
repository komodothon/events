from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user

def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You need to login to access this page.", "danger")
                return redirect(url_for("auth.login"))
            if current_user.role_name != role_name:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("events.home"))
            return func( *args, **kwargs)
        return wrapped_function
    return decorator


