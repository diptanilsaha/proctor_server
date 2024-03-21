from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

class CandidateAssessmentForm(FlaskForm):
    submission = FileField('Upload (ZIP File only)', [
        FileRequired(),
        FileAllowed(['zip', 'rar', '7zip'], 'Zip Files only!')
    ])
