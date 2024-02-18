import csv
from io import StringIO
from flask_login import login_required, current_user
from flask import redirect, url_for, flash, request, render_template
from proctor.assessments.forms import AddCandidatesForm
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment, Candidate, AssessmentStatus
from .add import validate_candidates

@assess_bp.route('/<pk>/add-candidates/', methods=['GET', 'POST'])
@login_required
def add_candidates(pk):
    assessment = db.get_or_404(Assessment, pk)

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

    form = AddCandidatesForm()
    if form.validate_on_submit():
        csv_file_data = request.files.get(form.candidates.name).read()
        if not validate_candidates(csv_file_data, assessment.lab, assessment=assessment):
            flash("Candidate List format is not correct or number of Candidates in list is \
                  greater than number of clients of the selected lab.", "error")
            return redirect(url_for('assessments.candidates', pk=assessment.id))
        rolls, succ_add = insert_candidates(csv_file_data, assessment)
        msg = "Candidates added successfully."
        if len(rolls) > 0:
            rolls_str = ', '.join(rolls)
            flash(f"{rolls_str} Roll Nos. already existed.", "message")
            if succ_add:
                msg = "Some " + msg
        if succ_add:
            flash(msg, "message")
        return redirect(url_for('assessments.candidates', pk=assessment.id))

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')

    return render_template(
        "assessments/add_candidates.html",
        title=f"Add Candidates via CSV - '{assessment.title}'",
        form=form,
        assessment=assessment
    )


def insert_candidates(csv_file_data: bytes, assessment: Assessment):
    # This method is different from the add.py's insert_candidate().
    # This one checks whether a roll number is already added or not.
    csvreader = csv.DictReader(StringIO(csv_file_data.decode('UTF-8')))
    rolls = []
    count = 0
    for row in csvreader:
        roll = row['Roll']
        name = row['Name']
        if validate_candidate(roll, assessment):
            Candidate.insert_candidate(name, roll, assessment)
            count += 1
        else:
            rolls.append(roll)
    return rolls, count


def validate_candidate(roll: str, assessment: Assessment):
    candidate = db.session.execute(
        db.select(Candidate).filter_by(
            roll=roll,
            assessment_id=assessment.id
        )
    ).scalar_one_or_none()

    if candidate is None:
        return True
    return False
