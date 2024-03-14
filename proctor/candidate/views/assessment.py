import os
from flask import flash, redirect, url_for, request, render_template, current_app
from sqlalchemy import and_
from proctor.models import (
    ClientSession,
    Assessment,
    AssessmentStatus,
    CandidateStatus
)
from proctor.candidate.form import CandidateAssessmentForm
from proctor.database import db
from proctor.utils import generate_media_name
from proctor.candidate.base import candidate_bp

@candidate_bp.route('/assessment/<pk>/', methods=['GET', 'POST'])
def assessment_view(pk: str):
    assessment = db.get_or_404(Assessment, pk)

    client_session = _get_remote_client(request.remote_addr)

    if _verify_client_session_and_assessment(
        assessment, client_session
    ):
        return redirect(url_for('candidate.index'))

    candidate = client_session.candidate

    if candidate.current_status in [CandidateStatus.PENDING, CandidateStatus.RESUBMIT]:
        form = CandidateAssessmentForm()

        if form.validate_on_submit():
            media_name = generate_media_name(form.media.data.filename)
            form.media.data.save(
                os.path.join(current_app.config['SUBMISSION_MEDIA'], media_name)
            )

            ctl = candidate.update_status(
                CandidateStatus.SUBMITTED,
                details='Candidate submitted work.'
            )

            candidate.submission_media_url = media_name
            db.session.add(ctl)
            db.session.commit()

            flash('Submitted successfully!')
            return redirect(url_for('candidate.assessment_view', pk=assessment.id))

        return render_template(
            "candidate/assessment.html",
            title='Candidate Assessment',
            assessment=assessment,
            form=form
        )

    return render_template(
        "candidate/assessment.html",
        title='Candidate Assessment',
        assessment=assessment,
    )


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
) -> bool :
    flag = True

    if not client_session:
        flag = False
        flash('ProctorClient not activated.', 'error')

    if client_session.candidate.assessment != assessment:
        flag = False
        flash('Candidate is not assigned to that assignment.', 'error')

    if assessment.current_status in [AssessmentStatus.INIT, AssessmentStatus.REG]:
        flag = False
        flash('Assessment is not active yet.', 'error')

    if not client_session.is_active:
        flag = False
        flash('ProctorClient is not active.', 'error')

    return flag
