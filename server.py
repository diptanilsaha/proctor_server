"""Proctor Server"""

from proctor import db, create_app
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
    CandidateTimeline,)

app = create_app()

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
