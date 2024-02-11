from flask import Blueprint

client_bp = Blueprint(
    'clients',
    import_name=__name__,
    url_prefix='/clients',
    template_folder='templates'
)
