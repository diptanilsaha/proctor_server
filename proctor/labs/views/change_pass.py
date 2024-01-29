"""Proctor Labs Change Password View"""
from flask_login import login_required
from flask import redirect, render_template, flash, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from proctor.database import db
from proctor.decorators import admin_required
from proctor.models import Lab
from proctor.labs.base import labs_bp

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', [
        DataRequired(), Length(min=8)
    ])
    confirm_password = PasswordField('Confirm password', [
        DataRequired(), EqualTo('password')
    ])

@labs_bp.route('/change_password/<int:pk>', methods=["GET", "POST"])
@login_required
@admin_required
def change_pass(pk):
    lab = db.get_or_404(Lab, int(pk))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        lab.user.set_password(form.password.data)
        db.session.commit()
        flash('Password Changed Successfully.', 'message')
        return redirect(url_for('labs.lab_view', lab_id=pk))

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')

    return render_template(
        'labs/change_pass.html',
        form=form,
        lab=lab,
        title='Change Password'
    )
