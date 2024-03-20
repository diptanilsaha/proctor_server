from flask import Blueprint

sessions_bp = Blueprint(
    'sessions',
    import_name=__name__,
    url_prefix='/session',
    template_folder="templates"
)
