import jwt
from sqlalchemy import func
from flask import request, jsonify, current_app
from proctor.clients.base import client_bp
from proctor.database import db
from proctor.models import Client

@client_bp.route('/register/', methods=['POST'])
def register_client():
    if request.method == 'POST':
        user_agent = request.headers.get('User-Agent')
        if 'ProctorAdminClient' not in user_agent:
            return jsonify({
                'status': 'error',
                'message': 'User-Agent not allowed.'
            }), 400
        content = request.json
        clientname = content['clientname']
        client = db.one_or_404(
            db.select(Client).filter_by(clientname=clientname)
        )
        if client.is_registered:
            return jsonify({
                'status': 'error',
                'message': 'Client is already registered.'
            }), 400
        client.is_registered = True
        client.registered_at = func.CURRENT_TIMESTAMP()
        db.session.commit()
        token = jwt.encode({
            'client_id': client.id
        }, key=current_app.config['SECRET_KEY'])
        return jsonify({
            'status': 'ok',
            'token': token,
            'message': 'Client Registered Successfully.'
        }),200
