from flask import flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment

@assess_bp.route('/candidates/<pk>/')
@login_required
def candidates(pk):
    assessment = db.get_or_404(Assessment, pk)

    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("You don't have permission to access.", "error")
            return redirect(url_for('assessments.index'))

    return render_template(
        "assessments/candidates.html",
        title=f"Candidates of '{assessment.title}'",
        assessment=assessment
    )
