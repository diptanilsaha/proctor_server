from sqlalchemy import and_
from typing import List
from proctor.database import db
from proctor.models import (
    Lab,
    Assessment,
    AssessmentStatus
)

def _get_active_assessments_by_lab(
    lab: Lab
) -> List[Assessment]:
    """
    Returns all Assessments which are in either REG, ACTIVE or BUFFER state
    held in a Lab.
    """
    assessments = db.session.execute(
        db.select(Assessment).filter(
            and_(
                Assessment.lab_id == lab.id,
                Assessment.current_status.in_([
                    AssessmentStatus.REG,
                    AssessmentStatus.ACTIVE,
                    AssessmentStatus.BUFFER
                ])
            )
        )
    ).scalars().all()

    return assessments

def _can_assessment_be_active(
    assessment: Assessment
) -> bool:
    """
    Checks if there are any live assessments under the same lab
    where the provided assessment is being held.
    """
    active_assessments = _get_active_assessments_by_lab(assessment.lab)

    if not len(active_assessments):
        return True

    if len(active_assessments) == 1:
        return assessment == active_assessments[0]

    return False

def _get_all_active_assessments() -> List[Assessment]:
    assessment = db.session.execute(
        db.select(Assessment).filter(
            Assessment.current_status.in_([
                AssessmentStatus.REG,
                AssessmentStatus.ACTIVE,
                AssessmentStatus.BUFFER
            ])
        )
    ).scalars().all()

    return assessment


def _check_assessment_is_active(assessment: Assessment) -> bool:
    active_assessments = _get_all_active_assessments()

    return assessment in active_assessments
