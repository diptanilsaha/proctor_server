"""Proctor Auth Base"""

from flask import Blueprint

auth_bp = Blueprint(
    'auth',
    import_name=__name__,
    url_prefix='/auth',
    template_folder="templates"
)
