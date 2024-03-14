from flask import Blueprint

candidate_bp = Blueprint(
    'candidate',
    import_name=__name__,
    url_prefix='/candidate',
    template_folder="templates"
)
