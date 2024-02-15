import os
import datetime
from flask_login import login_required, current_user
from flask import render_template, flash, redirect, url_for, current_app, request
from sqlalchemy import between, and_, or_
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.assessments.forms import UpdateAssessmentForm
from proctor.models import Assessment
from proctor.utils import generate_media_name, remove_assessment_media

@assess_bp.route('/update/<pk>/', methods=['GET', 'POST'])
@login_required
def update(pk):
    assessment = db.get_or_404(Assessment, pk)
    if not current_user.is_admin:
        if current_user.lab != assessment.lab:
            flash("You can update assessments which are held on your Lab.")
            return redirect(url_for("assessments.index"))

    form = UpdateAssessmentForm(obj=assessment)
    if not current_user.is_admin:
        form.lab_id.choices = [
            ('', "Select Lab"),
            (current_user.lab.id, current_user.lab.labname)
        ]
    if request.method == 'POST':
        if form.validate_on_submit():
            if not validate_form(
                assesment_id=assessment.id,
                start_time=form.start_time.data,
                duration=form.duration.data,
                lab_id=form.lab_id.data
            ):
                flash("Start Time or Duration error.")
                return redirect(url_for("assessments.update", pk=assessment.id))
            start_time = form.start_time.data
            end_time = start_time + datetime.timedelta(minutes=form.duration.data)
            assessment.title = form.title.data
            assessment.description = form.description.data
            assessment.lab_id = form.lab_id.data
            assessment.start_time = form.start_time.data
            assessment.end_time = end_time
            if form.media.data != assessment.media:
                media_name = generate_media_name(form.media.data.filename)
                form.media.data.save(
                    os.path.join(current_app.config['ASSESSMENT_MEDIA'], media_name)
                )
                remove_assessment_media(assessment.media)
                assessment.media = media_name
            db.session.commit()
            flash("Assessment updated successfully!", "message")
            return redirect(url_for('assessments.assessment_view',pk=assessment.id))
        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(err, 'error')

    return render_template(
        "assessments/update.html",
        title=f"Update '{assessment.title}'",
        form=form,
        assessment=assessment
    )

def validate_form(
    assesment_id: str,
    start_time: datetime.datetime,
    duration: int,
    lab_id: int,
) -> bool:
    if start_time < datetime.datetime.now():
        return False
    end_time = start_time + datetime.timedelta(minutes=duration)
    assessments = db.session.execute(
        db.select(Assessment).where(
            and_(
                and_(
                    or_(
                        between(
                            start_time,
                            Assessment.start_time,
                            Assessment.end_time
                        ),
                        between(
                            end_time,
                            Assessment.start_time,
                            Assessment.end_time
                        )
                    ),
                    Assessment.lab_id == lab_id
                ),
                Assessment.id != assesment_id,
            )
        )
    ).scalars().all()
    if len(assessments):
        return False
    return True
