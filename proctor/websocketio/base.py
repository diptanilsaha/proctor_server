from flask import Blueprint

socketio_bp = Blueprint(
    'socketio',
    import_name=__name__
)
