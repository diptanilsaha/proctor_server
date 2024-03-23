import os
from flask import flash, redirect, url_for, request, render_template, current_app, jsonify
from sqlalchemy import and_
from proctor.models import (
    ClientSession,
    Assessment,
    Candidate,
    AssessmentStatus,
    CandidateStatus
)
from proctor.candidate.form import CandidateAssessmentForm
from proctor.database import db
from proctor.utils import generate_media_name
from proctor.candidate.base import candidate_bp

@candidate_bp.route('/<pk>/', methods=['GET', 'POST'])
def assessment_view(pk: str):
    client_session = _get_remote_client(request.remote_addr)

    if not client_session:
        return render_template(
            "candidate/client_not_found.html",
            title="Client not found"
        )

    candidate = db.get_or_404(Candidate, pk)

    verify = _verify_client_session_and_assessment(
        candidate.assessment, client_session
    )
    if verify:
        flash(verify, 'error')
        return redirect(url_for('candidate.index'))

    if candidate.current_status in [CandidateStatus.PENDING, CandidateStatus.RESUBMIT]:

        if candidate.assessment.current_status in [
            AssessmentStatus.INIT,
            AssessmentStatus.REG,
            AssessmentStatus.COMPLETE,
            AssessmentStatus.EXPIRED
        ]:
            flash("Sorry, assessment is not active.", "error")
            return redirect(url_for('candidate.index'))

        form = CandidateAssessmentForm()

        if form.validate_on_submit():
            media_name = generate_media_name(form.submission.data.filename)
            form.submission.data.save(
                os.path.join(current_app.config['SUBMISSION_MEDIA'], media_name)
            )

            ctl = candidate.update_status(
                status=CandidateStatus.SUBMITTED,
                details='Candidate submitted work.'
            )

            candidate.submission_media_url = media_name
            db.session.add(ctl)
            db.session.commit()

            flash('Submitted successfully!')
            return redirect(url_for('candidate.assessment_view', pk=candidate.id))

        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(err, 'error')

        return render_template(
            "candidate/assessment.html",
            title='Candidate Assessment',
            candidate=candidate,
            client_session=client_session,
            form=form
        )


    return render_template(
        "candidate/assessment.html",
        title='Candidate Assessment',
        candidate=candidate,
        client_session=client_session,
    )

@candidate_bp.route('/<pk>/data/', methods=['GET', 'POST'])
def assessment_data(pk: str):
    client_session = _get_remote_client(request.remote_addr)

    if not client_session:
        return jsonify({
            'status': 'error'
        }), 400

    candidate = db.get_or_404(Candidate, pk)

    verify = _verify_client_session_and_assessment(
        candidate.assessment, client_session
    )

    if verify:
        flash(verify, 'error')
        return redirect(url_for('candidate.index'))

    data = {
        'assessment': {
            'currentStatus': candidate.current_status.name
        }
    }

    return jsonify(data), 200

def _get_remote_client(ip_addr: str) -> None | ClientSession:
    client_session: ClientSession = db.session.execute(
        db.select(ClientSession).filter(
            and_(
                ClientSession.is_active == True,
                ClientSession.session_ip_addr == ip_addr,
            )
        )
    ).scalar_one_or_none()

    return client_session

def _verify_client_session_and_assessment(
    assessment: Assessment,
    client_session: ClientSession
) -> str | None:

    if not client_session:
        return 'ProctorClient not activated.'

    if client_session.candidate.assessment != assessment:
        return 'Candidate is not assigned to that assignment.'

    if assessment.current_status in [AssessmentStatus.INIT, AssessmentStatus.REG]:
        return 'Assessment is not active yet.'

    if assessment.current_status in [AssessmentStatus.COMPLETE, AssessmentStatus.EXPIRED]:
        return 'Assessment either completed or expired.'

    if not client_session.is_active:
        return 'ProctorClient is not active.'
