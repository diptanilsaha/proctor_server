"""Proctor Lab View"""
from flask_login import login_required
from flask import render_template
from proctor.labs.base import labs_bp
from proctor.decorators import admin_required
from proctor.database import db
from proctor.models import Lab


@labs_bp.route('/<int:lab_id>')
@login_required
@admin_required
def lab_view(lab_id: int):
    lab = db.get_or_404(Lab, int(lab_id))
    return render_template(
        'labs/lab.html',
        title=lab.labname,
        lab=lab
    )
