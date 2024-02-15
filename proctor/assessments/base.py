from flask import Blueprint

assess_bp = Blueprint(
    "assessments",
    import_name=__name__,
    url_prefix='/assessments',
    template_folder='templates'
)
