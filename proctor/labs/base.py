"""Proctor Labs Base"""

from flask import Blueprint

labs_bp = Blueprint(
    'labs',
    import_name=__name__,
    url_prefix='/labs',
    template_folder="templates"
)
