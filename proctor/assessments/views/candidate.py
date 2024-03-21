from flask import flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Candidate, CandidateStatus
from proctor.assessments.forms import AcceptRejectSubmissionForm
from proctor.utils import remove_submission_media

@assess_bp.route('/candidate/<pk>/', methods=['GET', 'POST'])
@login_required
def candidate_view(pk):
    candidate: Candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("You don't have permission to access.", "error")
            return redirect(url_for('assessments.index'))

    if candidate.submission_media_url \
        and candidate.current_status == CandidateStatus.SUBMITTED:
        form = AcceptRejectSubmissionForm()

        if form.validate_on_submit():

            status = CandidateStatus.RESUBMIT
            details = f"{current_user.username} rejected submission."

            if not int(form.accept_reject.data):
                remove_submission_media(candidate.submission_media_url)
                candidate.submission_media_url = None

            if int(form.accept_reject.data):
                candidate.sub_verified_by = current_user

                status = CandidateStatus.VERIFIED
                details = f"{current_user.username} accepted submission."

            ctl_verified = candidate.update_status(
                status=status,
                details=details
            )

            db.session.add(ctl_verified)
            db.session.commit()

            flash("Candidate Submission scrutinized successfully.")
            return redirect(url_for('assessments.candidate_view', pk=candidate.id))

        return render_template(
            "assessments/candidate.html",
            title="Candidate",
            candidate=candidate,
            form=form
        )


    return render_template(
        "assessments/candidate.html",
        title="Candidate",
        candidate=candidate
    )
