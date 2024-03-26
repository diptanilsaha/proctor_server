import datetime
from typing import List
from .database import db
from .models import (
    User,
    Assessment,
    AssessmentStatus,
    AssessmentTimeline
)

def expire_assessments_job():
    with db.app.app_context():
        robot_user = db.session.execute(
            db.select(User).filter_by(username='proctorBot')
        ).scalar_one_or_none()
        assessments: List[Assessment] = db.session.execute(
            db.select(Assessment).filter(
                Assessment.current_status == AssessmentStatus.INIT,
                Assessment.end_time < datetime.datetime.now() - datetime.timedelta(seconds=300)
            )
        ).scalars().all()

        for assessment in assessments:
            assessment.current_status = AssessmentStatus.EXPIRED
            atl = AssessmentTimeline(
                status = AssessmentStatus.EXPIRED,
                assessment = assessment,
            )
            atl.atl_created_by = robot_user
            db.session.add(atl)
            db.session.commit()
