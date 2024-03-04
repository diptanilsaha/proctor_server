import jwt
import ipaddress
from flask import current_app, request
from proctor.extensions import socketio
from proctor.database import db
from proctor.models import (
    Client,
    ClientSession,
    ClientSessionTimeline,
    ClientSessionTLStatus
)

def validate_ip_address(ip_address: str) -> bool:
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def get_client_from_token(token: str) -> bool:
    client_from_token = jwt.decode(
        token,
        key=current_app.config['SECRET_KEY'],
        algorithms=["HS256",]
    )
    print(client_from_token)
    client = db.session.get(Client, client_from_token['client_id'])
    return client

@socketio.on('connect')
def connect(auth):
    client = get_client_from_token(auth['token'])

    if client is None:
        raise ConnectionRefusedError('Token not valid.')

    if not validate_ip_address(auth['ip_address']):
        raise ConnectionRefusedError('IP Address not valid.')


    client_session = ClientSession()
    client_session.session_ip_addr = auth['ip_address']
    client_session.session_id = request.sid
    client_session.client = client

    cs_tl = ClientSessionTimeline()
    cs_tl.client_session = client_session
    cs_tl.status = ClientSessionTLStatus.CC
    cs_tl.details = f"{client_session.client.clientname} connected."

    db.session.add_all([client_session, cs_tl])
    db.session.commit()
