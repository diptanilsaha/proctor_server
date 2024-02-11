from flask_login import login_required, current_user
from flask import render_template, request
from proctor.clients.base import client_bp
from proctor.models import Client, Lab
from proctor.database import db

@client_bp.route('/')
@login_required
def index():
    lab = None
    if current_user.is_admin:
        if 'lab' in request.args:
            labname = request.args.get('lab')
            lab = db.one_or_404(
                db.select(Lab).filter_by(labname=labname)
            )
            clients = lab.clients
        else:
            clients = db.session.query(Client).all()
    else:
        clients = db.session.query(Client).filter_by(
            lab_id = current_user.lab_id
        ).all()
    return render_template(
        "clients/index.html",
        clients=clients,
        lab=lab,
        title="Clients"
    )
