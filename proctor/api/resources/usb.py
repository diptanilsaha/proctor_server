from flask_restful import Resource, reqparse
from proctor.websocketio.utils import get_client_from_token
from proctor.database import db
from proctor.models import ClientSessionTimeline, ClientSessionTLStatus
from .errors import custom_error

parser = reqparse.RequestParser()
parser.add_argument(
    'token',
    type = str,
    required = True,
    help = "token cannot be blank!"
)
parser.add_argument(
    'status',
    type = str,
    required = True,
    help = "status cannot be blank!"
)
parser.add_argument(
    'details',
    type = str,
    required = True,
    help = "details cannot be blank!"
)
parser.add_argument(
    'User-Agent',
    location='headers'
)

class UsbIncident(Resource):
    def post(self):

        args = parser.parse_args()

        client = get_client_from_token(args['token'])
        details = args['details']
        status = args['status']
        user_agent = args['User-Agent']

        if user_agent != 'ProctorAdminClient':
            error_msg = {
                'status': 'error',
                'message': 'User-Agent mismatch.'
            }
            return custom_error(error_msg, 400)

        if client is None:
            error_msg = {
                'status': 'error',
                'message': 'client not found.',
            }
            return custom_error(error_msg, 404)

        if status not in ['connection', 'disconnection']:
            error_msg = {
                'status': 'error',
                'message': f"'{status}' not expected in status.",
            }
            return custom_error(error_msg, 500)

        if not client.is_active:
            error_msg = {
                'status': 'error',
                'message': "usb incident cannot be reported for a non-active client.",
            }
            return custom_error(error_msg, 400)

        client_session = client.client_sessions[0]

        cs_tl = ClientSessionTimeline()
        cs_tl.client_session = client_session
        cs_tl.requires_attention = True
        cs_tl.details = details
        cs_tl.status = ClientSessionTLStatus.UC
        if status == 'disconnection':
            cs_tl.status = ClientSessionTLStatus.UD
        db.session.add(cs_tl)
        db.session.commit()

        message = {
            'status': 'ok',
            'message': 'incident reported.'
        }
        return message, 201
