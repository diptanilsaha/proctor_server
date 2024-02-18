from flask_login import current_user, login_required
from flask import flash, redirect, url_for
from proctor.assessments.base import assess_bp
from proctor.models import Candidate, AssessmentStatus, Assessment
from proctor.database import db

@assess_bp.route('/delete-candidate/<pk>/', methods=['POST'])
@login_required
def delete_candidate(pk):
    candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("Sorry, you cannot access.", "error")
            return redirect(url_for('assessments.assessment_view', pk=candidate.assessment_id))

        if candidate.assessment.current_status != AssessmentStatus.INIT:
            flash("After Initial phase, Candidates can be deleted only by Admin", "error")
            return redirect(url_for('assessments.assessment_view', pk=candidate.assessment_id))

    if candidate.assessment.current_status not in [
        AssessmentStatus.INIT,
        AssessmentStatus.REG
    ]:
        flash("Candidates cannot be deleted after Registration Phase.", "error")
        return redirect(url_for('assessments.assessment_view', pk=candidate.assessment_id))

    assessment_id = candidate.assessment_id
    db.session.delete(candidate)
    db.session.commit()
    flash("Candidate deleted successfully.")
    return redirect(url_for('assessments.candidates', pk=assessment_id))


@assess_bp.route('/delete_all_candidates/<pk>/', methods=['POST'])
@login_required
def delete_all_candidates(pk):
    assessment = db.get_or_404(Assessment, pk)

    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("Sorry, you cannot access.", "error")
            return redirect(url_for('assessments.candidates', pk=assessment.id))

        if assessment.current_status != AssessmentStatus.INIT:
            flash("After Initial phase, Candidates can be deleted only by Admin", "error")
            return redirect(url_for('assessments.candidates', pk=assessment.id))

    if assessment.current_status not in [
        AssessmentStatus.INIT,
        AssessmentStatus.REG
    ]:
        flash("Candidates cannot be deleted after Registration Phase.", "error")
        return redirect(url_for('assessments.candidates', pk=assessment.id))

    msg = "No Candidates."
    if len(assessment.candidates) > 0:
        for candidate in assessment.candidates:
            db.session.delete(candidate)
            db.session.commit()
        msg = "Candidates deleted successfully!"

    flash(msg)
    return redirect(url_for('assessments.candidates', pk=assessment.id))
