from flask_login import login_required, current_user
from flask import request, render_template
from proctor.assessments.base import assess_bp
from proctor.database import db
from proctor.models import Assessment, Lab

@assess_bp.route('/')
@login_required
def index():
    lab = None
    if current_user.is_admin:
        if 'lab' in request.args:
            labname = request.args.get('lab')
            lab = db.one_or_404(
                db.select(Lab).filter_by(labname=labname)
            )
            assessments = db.session.query(Assessment).filter_by(
                lab_id=lab.id
            ).all()
        else:
            assessments = db.session.query(Assessment).all()
    else:
        assessments = db.session.query(Assessment).filter_by(
            lab_id=current_user.lab_id
        ).all()
    return render_template(
        'assessments/index.html',
        lab=lab,
        assessments=assessments,
        title='Assessments'
    )
