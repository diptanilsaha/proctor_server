import datetime
from flask import request
from proctor.extensions import socketio
from proctor.database import db
from proctor.models import (
    ClientSession,
    ClientSessionTimeline,
    ClientSessionTLStatus
)

@socketio.on('disconnect')
def disconnect():
    client_session: ClientSession = db.session.execute(
        db.select(ClientSession).filter_by(session_id = request.sid)
    ).scalar_one_or_none()

    if client_session is None:
        return

    deactivate_client_session(client_session)
    db.session.commit()


def deactivate_client_session(
    client_session: ClientSession,
    reconnection: bool = False
) -> None:
    """Deactivates Client Session. Please commit after using this method."""
    client_session.is_active = False
    client_session.session_end_time = datetime.datetime.now().replace(microsecond=0)

    msg = f"{client_session.client.name} disconnected."
    status = ClientSessionTLStatus.CDWRT
    attention_required = False

    if not client_session.can_terminate:
        msg = f"{client_session.client.name} disconnected without termination."
        status = ClientSessionTLStatus.CDWOTR
        attention_required = True

    if reconnection:
        msg = msg + " during reconnection."

    cs_tl = ClientSessionTimeline()
    cs_tl.client_session = client_session
    cs_tl.details = msg
    cs_tl.status = status
    cs_tl.requires_attention = attention_required

    db.session.add(cs_tl)
