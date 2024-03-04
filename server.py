"""Proctor Server"""
import os
from flask import Flask
from proctor.extensions import login_manager, scheduler, socketio
from proctor.config import Config
from proctor.database import db, migrate
from proctor.models import (
    User,
    Role,
    Lab,
    Assessment,
    Client,
    ClientSession,
    ClientSessionTimeline,
    AssessmentTimeline,
    Candidate,
    CandidateTimeline,
)
from proctor.labs.base import labs_bp
from proctor.auth.base import auth_bp
from proctor.clients.base import client_bp
from proctor.assessments.base import assess_bp
from proctor.cli import cli_bp
from proctor.websocketio.base import socketio_bp

def create_app(
    debug: bool = False,
    config_class: Config = Config
) -> Flask:
    """Proctor Flask App."""
    app = Flask(__name__)
    app.debug = debug
    app.config.from_object(config_class)

    if not os.path.exists(app.config['ASSESSMENT_MEDIA']):
        os.mkdir(app.config['ASSESSMENT_MEDIA'])

    init_db(app)
    init_login(app)
    init_scheduler(app)
    init_socketio(app)

    register_blueprints(app)

    @app.shell_context_processor
    def make_shell_context():
        """Adding Database Models in Shell Context."""
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Lab': Lab,
            'Assessment': Assessment,
            'Client': Client,
            'ClientSession': ClientSession,
            'ClientSessionTimeline': ClientSessionTimeline,
            'AssessmentTimeline': AssessmentTimeline,
            'Candidate': Candidate,
            'CandidateTimeline': CandidateTimeline,
        }

    return app

def init_db(app : Flask):
    """Initialize SQLAlchemy and Migrate"""
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)

def init_login(app: Flask):
    """Initialize Flask-Login and user_loader"""
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

def register_blueprints(app: Flask):
    """Register all the Blueprints."""
    app.register_blueprint(labs_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(assess_bp)
    app.register_blueprint(cli_bp)
    app.register_blueprint(socketio_bp)

def init_scheduler(app: Flask):
    scheduler.init_app(app)
    scheduler.start()

def init_socketio(app: Flask):
    socketio.init_app(app)
