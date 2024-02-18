from flask import flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Candidate

@assess_bp.route('/candidate/<pk>/')
@login_required
def candidate_view(pk):
    candidate: Candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("You don't have permission to access.", "error")
            return redirect(url_for('assessments.index'))

    return render_template(
        "assessments/candidate.html",
        title="Candidate",
        candidate=candidate
    )
