from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
from proctor.database import db
from proctor.models import Lab

def get_all_labs():
    all_labs = db.session.query(Lab).all()
    choices = [('', 'Select Lab')]
    for lab in all_labs:
        choices.append((lab.id, lab.labname))
    return choices

class AddClientForm(FlaskForm):
    name = StringField("Name", [DataRequired(), Length(min=3, max=40)])
    lab = SelectField("Lab", choices=get_all_labs, validators=[DataRequired()])
