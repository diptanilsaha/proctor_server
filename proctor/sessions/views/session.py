from flask_login import login_required
from flask import render_template
from proctor.sessions.base import sessions_bp
from proctor.models import ClientSession
from proctor.database import db

@sessions_bp.route('/<session_id>/')
@login_required
def session(session_id):
    client_session = db.get_or_404(ClientSession, session_id)

    return render_template(
        "sessions/session.html",
        title="Client Session",
        client_session=client_session
    )
