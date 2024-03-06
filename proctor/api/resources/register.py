import jwt
from flask import current_app
from flask_restful import reqparse, Resource
from sqlalchemy import func
from proctor.database import db
from proctor.models import Client
from .errors import custom_error

parser = reqparse.RequestParser()
parser.add_argument(
    'client_name',
    type = str,
    required = True,
    help = "client_name cannot be blank."
)
parser.add_argument(
    'User-Agent',
    location = 'headers'
)

class ClientRegister(Resource):
    def post(self):
        args = parser.parse_args()

        user_agent = args['User-Agent']
        client_name = args['client_name']

        if user_agent != 'ProctorAdminClient':
            error_msg = {
                'status': 'error',
                'message': 'User-Agent mismatch.'
            }
            return custom_error(error_msg, 400)

        client: Client = db.session.execute(
            db.select(Client).filter_by(clientname = client_name)
        ).scalar_one_or_none()

        if client is None:
            error_msg = {
                'status': 'error',
                'message': 'client not found.'
            }
            return custom_error(error_msg, 404)

        if client.is_registered:
            error_msg = {
                'status': 'error',
                'message': 'Client is already registered.'
            }
            return custom_error(error_msg, 400)

        client.is_registered = True
        client.registered_at = func.CURRENT_TIMESTAMP()

        db.session.commit()

        token = jwt.encode({
            'client_id': client.id
        }, key=current_app.config['SECRET_KEY'])

        message = {
            'status': 'ok',
            'token': token,
            'message': 'client registered successfully.'
        }

        return message, 201
