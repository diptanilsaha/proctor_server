import os
import csv
import datetime
from io import StringIO
from flask_login import login_required, current_user
from flask import request, current_app, render_template, flash, redirect, url_for
from proctor.assessments.base import assess_bp
from proctor.models import Assessment, Candidate
from proctor.assessments.forms import AddAssessmentForm
from proctor.utils import generate_media_name

@assess_bp.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    form = AddAssessmentForm()
    min_time = datetime.datetime.now().strftime(r"%Y-%m-%dT%H:%M")
    if not current_user.is_admin:
        form.lab_id.choices = [
            ('', "Select Lab"),
            (current_user.lab.id, current_user.lab.labname)
        ]
    if request.method == 'POST':
        if form.validate_on_submit():
            candidate_data = request.files.get(form.candidate.name).read()
            if form.candidate.data and not validate_candidates(candidate_data):
                flash("Candidate List format is not correct.")
                return redirect(url_for('assessments.add'))
            end_time = form.start_time.data + datetime.timedelta(minutes=form.duration.data)
            media_name = generate_media_name(form.media.data.filename)
            assessment = Assessment.insert_assessment(
                title=form.title.data,
                description=form.description.data,
                media=media_name,
                lab_id=form.lab_id.data,
                start_time=form.start_time.data,
                end_time=end_time,
                user=current_user
            )
            form.media.data.save(
                os.path.join(current_app.config['ASSESSMENT_MEDIA'], media_name)
            )
            if form.candidate.data:
                flag = insert_candidates(candidate_data, assessment)
                if not flag:
                    flash('Candidate List could not be inserted.', 'error')
                else:
                    flash('Candidate List inserted successfully added.', 'message')
            flash('Assessment created successfully.', 'message')
            return redirect(url_for('assessments.index'))
        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(err, 'error')

    return render_template(
        'assessments/add.html',
        title='Add Assessments',
        min_time=min_time,
        form=form,
    )

def validate_candidates(candidate_file_stream: bytes):
    csvreader = csv.DictReader(StringIO(candidate_file_stream.decode('UTF-8')))
    csv_fields = list(csvreader.fieldnames)
    fields = ['Name', 'Roll']
    csv_fields.sort()
    if fields != csv_fields:
        return False
    roll = []
    for row in csvreader:
        roll.append(row['Roll'])
    if len(roll) != len(set(roll)):
        return False
    return True

def insert_candidates(candidate_file_stream: bytes, assessment: Assessment):
    csvreader = csv.DictReader(StringIO(candidate_file_stream.decode('UTF-8')))
    for row in csvreader:
        roll = row['Roll']
        name = row['Name']
        Candidate.insert_candidate(name, roll, assessment)

    return True
