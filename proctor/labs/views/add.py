"""Proctor - Add Labs View"""
import re
from flask_login import login_required
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, \
    Length, EqualTo, ValidationError
from flask_wtf import FlaskForm
from flask import flash, render_template, redirect, url_for
from proctor.labs.base import labs_bp
from proctor.database import db
from proctor.decorators import admin_required
from proctor.models import User, Role, Lab, RoleName

def validate_lab_mod_username(form, field):
    username = str(field.data).strip()
    regex = re.compile('[^a-z0-9_]')
    if bool(regex.search(username)):
        raise ValidationError(
            'Lab Mod Username can contain \'_\', smallcase and numeric characters'
        )

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if user is not None:
        raise ValidationError('Username already exists.')

def validate_lab_name(form, field):
    labname = str(field.data).strip()
    regex = re.compile(r'[^a-zA-Z0-9\s]')
    if bool(regex.search(labname)):
        raise ValidationError(
            'Lab Name can contain Space and Alphanumeric characters'
        )
    lab = db.session.execute(
        db.select(Lab).filter_by(labname=labname)
    ).scalar_one_or_none()

    if lab is not None:
        raise ValidationError('Lab already exists.')

class AddLab(FlaskForm):
    labname = StringField("Lab Name", [
        DataRequired(), Length(min=1, max=40), validate_lab_name
    ])
    labmod_username = StringField("Lab Mod Username", [
        DataRequired(), Length(min=1, max=10), validate_lab_mod_username
    ])
    password = PasswordField("Password", [
        DataRequired(), Length(min=8)
    ])
    confirm_password = PasswordField("Confirm Password", [
        DataRequired(), EqualTo('password', message='Password does not match')
    ])


@labs_bp.route('/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lab():
    form = AddLab()
    if form.validate_on_submit():
        lab_mod = db.session.execute(
            db.select(Role).filter_by(name=RoleName.LAB_MOD)
        ).scalar_one()
        lab = Lab(
            labname=str(form.labname.data).strip(),
        )
        user = User(
            username=str(form.labmod_username.data).strip().lower(),
            lab=lab,
            role=lab_mod,
        )
        user.set_password(form.password.data)
        db.session.add_all([user, lab])
        db.session.commit()
        flash('Lab created successfully.', 'message')
        return redirect(url_for('labs.index'))

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')

    return render_template(
        'labs/add.html',
        form=form,
        title='Add New Lab'
    )
