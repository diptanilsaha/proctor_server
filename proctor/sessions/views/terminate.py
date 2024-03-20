from flask_login import login_required, current_user
from flask import flash, redirect, url_for
from proctor.sessions.base import sessions_bp
from proctor.database import db
from proctor.models import (
    ClientSession,
    ClientSessionTimeline,
    ClientSessionTLStatus
)

@sessions_bp.route('/terminate/<pk>/', methods=['POST'])
@login_required
def terminate(pk):
    client_session = db.get_or_404(ClientSession, pk)

    if not client_session.is_active:
        flash('Only active clients can be allowed to Terminate.', 'error')
        return redirect(url_for('sessions.session', session_id=pk))

    if client_session.can_terminate:
        flash("Client Session already marked as 'Allowed to Terminate'", 'error')
        return redirect(url_for('sessions.session', session_id=pk))

    client_session.can_terminate = True

    cs_tl = ClientSessionTimeline()
    cs_tl.client_session = client_session
    cs_tl.status = ClientSessionTLStatus.TR
    cs_tl.details = f"Allow to terminate requested by {current_user.username}."

    db.session.add(cs_tl)
    db.session.commit()

    return redirect(url_for('session.session', session_id=pk))
