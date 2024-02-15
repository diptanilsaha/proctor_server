from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment, AssessmentStatus
from proctor.utils import remove_assessment_media

@assess_bp.route('/delete/<pk>/', methods=['POST'])
@login_required
def delete(pk):
    assessment = db.get_or_404(Assessment, pk)
    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("Assessment can be deleted, which are held at your lab.", "error")
            return redirect(url_for('assessments.index'))

    if assessment.current_status not in [AssessmentStatus.INIT, AssessmentStatus.COMPLETE]:
        flash("Assessment can be deleted only at initial or complete phase.", "error")
        return redirect(url_for("assessments.index"))
    filename = assessment.media
    db.session.delete(assessment)
    db.session.commit()
    if not remove_assessment_media(filename):
        flash('Assessment Media File could not be deleted.', 'error')
    flash('Assessment deleted successfully!', 'message')
    return redirect(url_for('assessments.index'))
