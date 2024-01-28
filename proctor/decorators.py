"""Proctor Decorators."""

from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(func):
    """
    If a view is decorated with this, it will ensure that the current user
    logged in must be a Administrator.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_view
