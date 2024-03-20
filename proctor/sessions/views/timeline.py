import datetime
from flask_login import login_required, current_user
from flask import render_template
from proctor.sessions.base import sessions_bp
from proctor.models import ClientSession
from proctor.database import db


@sessions_bp.route('/<session_id>/timeline/')
@login_required
def timeline(session_id):
    client_session = db.get_or_404(ClientSession, session_id)

    cs_timeline = client_session.session_timeline

    # if any timeline row requires attention and the difference of current time and
    # timestamp of the row is less than 60 minutes then the first user who visits the
    # timeline page is marked as the user attended for the row which requires attention.
    for row in cs_timeline:
        if row.requires_attention and row.attended_by is None and \
            datetime.datetime.now() - row.timestamp < datetime.timedelta(minutes=60):
            row.attended_by = current_user

    db.session.commit()

    return render_template(
        "sessions/timeline.html",
        title="Session Timeline",
        client_session = client_session,
        cs_timeline = cs_timeline
    )
