from flask_login import login_required, current_user
from flask import redirect, url_for, flash, render_template
from proctor.assessments.base import assess_bp
from proctor.assessments.forms import AddCandidateForm
from proctor.database import db
from proctor.models import Assessment, Candidate, AssessmentStatus
from .add_candidates import validate_candidate

@assess_bp.route('/<pk>/add-candidate/', methods=['GET', 'POST'])
@login_required
def add_candidate(pk):
    assessment: Assessment = db.get_or_404(Assessment, pk)

    if len(assessment.lab.clients) <= len(assessment.candidates):
        flash("No more candidates can be added.", "error")
        return redirect(url_for("assessments.candidates", pk=assessment.id))

    if assessment.current_status in [
        AssessmentStatus.EXPIRED,
        AssessmentStatus.COMPLETE,
        AssessmentStatus.BUFFER
    ]:
        flash(
            "Candidates cannot be added to the Assessments \
            that have already expired or completed or present in buffer phase.",
            "error"
        )
        return redirect(url_for("assessments.candidates", pk=assessment.id))

    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("Sorry, you cannot access!", "error")
            return redirect(url_for("assessments.index"))
        if assessment.current_status not in [
            AssessmentStatus.INIT,
            AssessmentStatus.REG
        ]:
            flash("Only admins can add candidates after Registration Phase.", "error")
            return redirect(url_for("assessments.candidates", pk=assessment.id))

    form = AddCandidateForm()
    if form.validate_on_submit():
        roll = form.roll.data.strip()
        name = form.name.data.strip()

        if not validate_candidate(roll, assessment):
            flash(f"Roll '{roll}' already exists.", "error")
            return redirect(url_for("assessments.add_candidate", pk=assessment.id))

        Candidate.insert_candidate(name, roll, assessment)
        flash("Candidate addedd successfully.", "message")
        return redirect(url_for("assessments.candidates", pk=assessment.id))

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')

    return render_template(
        "assessments/add_candidate.html",
        title=f"Add a Candidate - '{assessment.title}'",
        form=form,
        assessment=assessment
    )
