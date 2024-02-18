import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from sqlalchemy import between, and_
from wtforms import (
    StringField,
    SelectField,
    IntegerField,
    TextAreaField,
    DateTimeLocalField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
    ValidationError
)
from proctor.database import db
from proctor.models import Lab, Assessment, ClientSession

def lab_choices():
    labs = db.session.query(Lab).all()
    choices = [("", 'Select Lab')]
    for lab in labs:
        choices.append((lab.id, f"{lab.labname} ({len(lab.clients)} clients)"))
    return choices


class AssessmentForm(FlaskForm):
    title = StringField('Title', [DataRequired(), Length(min=5, max=50)])
    description = TextAreaField('Description/Instruction', [DataRequired()])
    lab_id = SelectField('Lab', choices=lab_choices, validators=[DataRequired()])
    start_time = DateTimeLocalField('Start Time', [DataRequired()])
    duration = IntegerField('Duration (in minutes)', [
        DataRequired(),
        NumberRange(min=0)
    ])

class AddAssessmentForm(AssessmentForm):
    media = FileField(
        'Reference Materials (pdf or zip file only)', [
            FileRequired(),
            FileAllowed(['pdf', 'zip','rar','7zip'], 'PDF or Zip Files Only!')
        ]
    )
    candidate = FileField('Candidates List (only csv file)', [
        Optional(),
        FileAllowed(['csv',], 'CSV Files Only!')
    ])

    def validate_start_time(form, field):
        if field.data < datetime.datetime.now():
            raise ValidationError("Start Time cannot be earlier than Current Time.")
        assessments = db.session.execute(
            db.select(Assessment).where(
                and_(
                    between(
                        field.data,
                        Assessment.start_time,
                        Assessment.end_time
                    ),
                    Assessment.lab_id == form.lab_id.data
                )
            )
        ).scalars().all()
        if len(assessments):
            raise ValidationError("Start Time is overlapping with other Assessments.")

    def validate_duration(form, field):
        end_time = form.start_time.data + datetime.timedelta(minutes=field.data)
        assessments = db.session.execute(
            db.select(Assessment).where(
                and_(
                    between(
                        end_time,
                        Assessment.start_time,
                        Assessment.end_time,
                    ),
                    Assessment.lab_id == form.lab_id.data
                )
            )
        ).scalars().all()

        if len(assessments):
            raise ValidationError("Duration is overlapping with other Assessments.")

class UpdateAssessmentForm(AssessmentForm):
    media = FileField(
        'Reference Materials (pdf or zip file only)', [
            Optional(),
            FileAllowed(['pdf', 'zip','rar','7zip'], 'PDF or Zip Files Only!')
        ]
    )

class AddCandidatesForm(FlaskForm):
    candidates = FileField("Candidate (CSV Files only)", [
        FileRequired(),
        FileAllowed(['csv'], "CSV File Only allowed")
    ])

class AddCandidateForm(FlaskForm):
    roll = StringField("Candidate Roll", [
        DataRequired(),
        Length(max=20, min=1)
    ])
    name = StringField("Candidate Name", [
        DataRequired(),
        Length(max=40, min=1)
    ])

class AssignCandidateForm(FlaskForm):
    client_session = SelectField(
        'Client',
        validators=[DataRequired()],
    )

    def validate_client_session(form, field):
        client: ClientSession = db.session.get(ClientSession, field.data)

        if client is None:
            raise ValidationError("Client Session not found.")

        if not client.is_active:
            raise ValidationError("Candidate can be assigned only to Active Client.")

        if client.candidate is not None:
            raise ValidationError("Candidate is already assigned on the selected Client.")
