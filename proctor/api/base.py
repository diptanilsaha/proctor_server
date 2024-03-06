from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint(
    'api',
    import_name=__name__,
    url_prefix="/api",
)

api = Api(api_bp)
