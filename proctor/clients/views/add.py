from flask_login import login_required, current_user
from flask import url_for, render_template, flash, redirect
from proctor.clients.base import client_bp
from proctor.decorators import admin_required
from proctor.clients.forms import AddClientForm
from proctor.models import Client
from proctor.database import db

@client_bp.route('/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = AddClientForm()
    if form.validate_on_submit():
        client = Client(
            name = form.name.data.strip(),
            lab_id = int(form.lab.data.strip()),
            created_by = current_user
        )
        db.session.add(client)
        db.session.commit()
        flash(f"{client.clientname} created successfully.", "message")
        return redirect(url_for('clients.index'))
    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')
    return render_template(
        "clients/add.html",
        form=form,
        title="Add Client"
    )
