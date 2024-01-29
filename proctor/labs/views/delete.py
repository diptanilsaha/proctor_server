"""Proctor Delete Lab View"""
from flask import redirect, url_for, flash
from flask_login import login_required
from proctor.labs.base import labs_bp
from proctor.decorators import admin_required
from proctor.database import db
from proctor.models import Lab

@labs_bp.route('/delete/<int:pk>/', methods=["POST"])
@login_required
@admin_required
def delete_lab(pk):
    lab: Lab = db.get_or_404(Lab, int(pk))
    if len(lab.clients) != 0:
        flash('Lab couldn\'t be deleted.', 'error')
        return redirect(url_for('labs.index'))
    db.session.delete(lab.user)
    db.session.delete(lab)
    db.session.commit()
    flash('Lab successfully deleted.', 'message')
    return redirect(url_for('labs.index'))
