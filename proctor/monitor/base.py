from flask import Blueprint

monitor_bp = Blueprint(
    'monitor',
    import_name=__name__,
    url_prefix="/monitor",
    template_folder="templates"
)
