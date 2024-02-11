from flask_login import login_required
from flask import flash, redirect, url_for
from proctor.clients.base import client_bp
from proctor.decorators import admin_required
from proctor.database import db
from proctor.models import Client

@client_bp.route('/delete/<pk>/', methods=['POST'])
@login_required
@admin_required
def delete_client(pk):
    client: Client = db.get_or_404(Client, pk)
    lab = client.lab
    if client.client_sessions and client.client_sessions[0].is_active:
        flash("Active Client cannot be deleted.", 'error')
        return redirect(url_for(
            'clients.client_view', clientname=client.clientname
        ))
    db.session.delete(client)
    db.session.commit()
    flash('Client successfully deleted.', 'message')
    return redirect(url_for(
        'clients.index', lab=lab.labname
    ))
