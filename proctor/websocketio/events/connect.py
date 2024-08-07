from flask import request
from proctor.extensions import socketio
from proctor.database import db
from proctor.models import (
    ClientSession,
    ClientSessionTimeline,
    ClientSessionTLStatus
)
from proctor.websocketio.utils import get_client_from_token
from .disconnect import deactivate_client_session

@socketio.on('connect')
def connect(auth):
    client = get_client_from_token(auth)

    if client is None:
        raise ConnectionRefusedError('Token not valid.')

    if client.is_active:
        client_session = client.client_sessions[0]
        deactivate_client_session(client_session, reconnection=True)

    client_session = ClientSession()
    client_session.session_ip_addr = request.remote_addr
    client_session.session_id = request.sid
    client_session.client = client

    cs_tl = ClientSessionTimeline()
    cs_tl.client_session = client_session
    cs_tl.status = ClientSessionTLStatus.CC
    cs_tl.details = f"{client_session.client.clientname} connected."

    db.session.add_all([client_session, cs_tl])
    db.session.commit()
