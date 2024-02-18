import datetime
from flask_login import login_required, current_user
from flask import redirect, url_for, flash
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment, AssessmentStatus, AssessmentTimeline

@assess_bp.route('/update_status/<pk>/', methods=['POST'])
@login_required
def update_status(pk):
    assessment = db.get_or_404(Assessment, pk)

    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("Sorry, you cannot access.", "error")
            return redirect(url_for('assessments.index'))

    current_status = assessment.current_status

    if current_status == AssessmentStatus.EXPIRED or \
        current_status == AssessmentStatus.COMPLETE:
        flash("Assessment either expired or marked as completed.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    time_now = datetime.datetime.now()

    if current_status == AssessmentStatus.REG:
        if len(assessment.candidates) == 0:
            flash("Assessment cannot be activated with Zero candidates.", "error")
            return redirect(url_for('assessments.assessment_view', pk=assessment.id))

        if not (time_now >= assessment.start_time and time_now <= assessment.end_time):
            flash("Assessment can be started only between Assessment's Time.", "error")
            return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    if current_status == AssessmentStatus.ACTIVE:
        if time_now >= assessment.start_time and time_now <= assessment.end_time:
            flash("Buffer Phase will be activated only after the Active Time.", "error")
            return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    next_status = None
    if current_status == AssessmentStatus.INIT:
        next_status = AssessmentStatus.REG
    elif current_status == AssessmentStatus.REG:
        next_status = AssessmentStatus.ACTIVE
    elif current_status == AssessmentStatus.ACTIVE:
        next_status = AssessmentStatus.BUFFER
    elif current_status == AssessmentStatus.BUFFER:
        next_status = AssessmentStatus.COMPLETE

    atl = AssessmentTimeline(
        status = next_status,
        atl_created_by = current_user,
        assessment = assessment
    )
    assessment.current_status = next_status
    db.session.add(atl)
    db.session.commit()
    flash("Assessment's Status Updated Successfully.")
    return redirect(url_for('assessments.assessment_view', pk=assessment.id))

@assess_bp.route('/revert_status/<pk>/', methods=['POST'])
@login_required
def revert_status(pk):
    assessment = db.get_or_404(Assessment, pk)
    if not current_user.is_admin:
        flash("Only Administrator's can use this functionality.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    prev_status = None
    current_status = assessment.current_status

    if current_status == AssessmentStatus.INIT:
        flash("Assessment's Status is at initial stage and cannot be reverted.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    if current_status == AssessmentStatus.EXPIRED \
        or current_status == AssessmentStatus.COMPLETE:
        flash("Assessment's Status cannot be reverted, once Expired or Marked Complete.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    if current_status == AssessmentStatus.ACTIVE:
        flash("Active Assessment cannot be reverted.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    if current_status == AssessmentStatus.BUFFER:
        flash("Assessment cannot be reverted from Buffer Phase.", "error")
        return redirect(url_for('assessments.assessment_view', pk=assessment.id))

    if current_status == AssessmentStatus.REG:
        prev_status = AssessmentStatus.INIT

    atl = AssessmentTimeline(
        status = prev_status,
        atl_created_by = current_user,
        assessment = assessment
    )
    assessment.current_status = prev_status
    db.session.add(atl)
    db.session.commit()
    flash("Assessment's Status Updated Successfully.")
    return redirect(url_for('assessments.assessment_view', pk=assessment.id))
