from flask_login import login_required, current_user
from flask import render_template, flash, redirect, url_for
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment

@assess_bp.route('/<pk>/')
@login_required
def assessment_view(pk):
    assessment = db.get_or_404(Assessment, pk)
    if not current_user.is_admin:
        if assessment.lab != assessment.lab:
            flash("Assessment not held at your lab, cannot be accessed.", "error")
            return redirect(url_for("assessments.index"))
    return render_template(
        "assessments/assessment.html",
        title=f"'{assessment.title}'",
        assessment=assessment
    )
