import jwt
from flask import current_app
from proctor.database import db
from proctor.models import Client

def get_client_from_token(token: str) -> Client | None:
    """Get client from Token."""
    client_from_token = jwt.decode(
        token,
        key=current_app.config['SECRET_KEY'],
        algorithms=["HS256",]
    )
    client = db.session.get(Client, client_from_token['client_id'])
    return client
