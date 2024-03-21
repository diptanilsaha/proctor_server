from flask import send_from_directory, current_app, abort, request
from proctor.candidate.base import candidate_bp
from flask_login import current_user
from .assessment import _get_remote_client

@candidate_bp.route('/submission/<filename>')
def submission_file(filename):
    client_session = _get_remote_client(request.remote_addr)

    if not current_user.is_authenticated:
        if client_session.candidate.submission_media_url != filename:
            abort(403)

    return send_from_directory(
        current_app.config['SUBMISSION_MEDIA'],
        filename,
        as_attachment=True
    )

@candidate_bp.route('/assessment_media/<filename>')
def assessment_media(filename):
    client_session = _get_remote_client(request.remote_addr)

    if not current_user.is_authenticated:
        if client_session.candidate.assessment.media != filename:
            abort(403)

    return send_from_directory(
        current_app.config['ASSESSMENT_MEDIA'],
        filename,
        as_attachment = True
    )
