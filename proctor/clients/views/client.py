from flask_login import login_required
from flask import render_template
from proctor.clients.base import client_bp
from proctor.database import db
from proctor.models import Client

@client_bp.route('/<clientname>/')
@login_required
def client_view(clientname):
    client = db.one_or_404(
        db.select(Client).filter_by(clientname=clientname)
    )
    return render_template(
        "clients/client.html",
        title=client.clientname,
        client=client,
    )
