from flask import render_template, request
from proctor.candidate.base import candidate_bp
from .assessment import _get_remote_client

@candidate_bp.route('/')
def index():
    client_session = _get_remote_client(request.remote_addr)

    if not client_session:
        return render_template(
            "candidate/client_not_found.html",
            title="Client not found"
        )

    return render_template(
        "candidate/index.html",
        title="Candidate",
        client_session=client_session,
        candidate=client_session.candidate
    )
