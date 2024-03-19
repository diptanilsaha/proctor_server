from typing import List
from flask import render_template, jsonify, url_for
from flask_login import login_required
from proctor.monitor.base import monitor_bp
from proctor.models import (
    Assessment,
    CandidateStatus,
    Candidate,
    AssessmentStatus
)
from proctor.database import db
from proctor.assessments.utils import _check_assessment_is_active

@monitor_bp.route('/<pk>/')
@login_required
def monitor_assessment_view(pk: str):
    assessment = db.get_or_404(Assessment, pk)

    return render_template(
        "monitor/monitor.html",
        title=f"Monitor {assessment.title}",
        assessment=assessment
    )

@monitor_bp.route('/<pk>/data/')
@login_required
def monitor_assessment_data(pk: str):
    assessment = db.get_or_404(Assessment, pk)
    active = _check_assessment_is_active(assessment)

    monitor_data = {}

    monitor_data['assessment'] = {
        'title': assessment.title,
        'current_status': assessment.current_status.name,
        'start_time': assessment.start_time,
        'end_time': assessment.end_time,
    }


    if not active:
        message = "assessment either finished or expired."
        if assessment.current_status == AssessmentStatus.INIT:
            message = "assessment not started yet."
        monitor_data['live'] = {
            'message': message
        }
        return jsonify(monitor_data)

    candidate_data_by_status = {
        'submitted': [],
        'resubmit': [],
        'pending': [],
        'verified': []
    }

    for candidate in assessment.candidates:

        if candidate.current_status == CandidateStatus.SUBMITTED:
            candidate_data_by_status['submitted'].append(candidate)
        elif candidate.current_status == CandidateStatus.RESUBMIT:
            candidate_data_by_status['resubmit'].append(candidate)
        elif candidate.current_status == CandidateStatus.VERIFIED:
            candidate_data_by_status['verified'].append(candidate)
        else:
            candidate_data_by_status['pending'].append(candidate)

    all_candidates_data: List[Candidate] = []

    all_candidates_data += candidate_data_by_status['submitted']
    all_candidates_data += candidate_data_by_status['resubmit']
    all_candidates_data += candidate_data_by_status['pending']
    all_candidates_data += candidate_data_by_status['verified']

    candidates = sorted(
        all_candidates_data,
        key = lambda d: d.client_session.requires_attention if d.client_session else False,
        reverse=True
    )

    monitor_data['live'] = {}

    monitor_data['live']['candidates'] = []

    req_attention_count = 0

    for candidate in candidates:
        client_name = 'Not Assigned'
        client_status = 'Not Assigned'
        requires_attention = False
        client_timeline_url = '#'

        if candidate.client_session:
            client_name = candidate.client_session.client.name
            client_status = candidate.client_session.session_timeline[0].status.name
            requires_attention = candidate.client_session.requires_attention
            if requires_attention:
                req_attention_count += 1
            client_timeline_url = url_for(
               'sessions.timeline', session_id=candidate.client_session.id
            )

        monitor_data['live']['candidates'].append({
            "candidateDetails": f"{candidate.roll} - {candidate.name}",
            "clientName": client_name,
            "clientStatus": client_status,
            "candidateStatus": candidate.current_status.name,
            "requiresAttention": requires_attention,
            "candidateUrl": url_for('assessments.candidate_view', pk=candidate.id),
            "clientTimelineUrl": client_timeline_url
        })

    monitor_data['live']['count'] = {
        'pending': len(candidate_data_by_status['pending']),
        'submitted': len(candidate_data_by_status['submitted']),
        'resubmit': len(candidate_data_by_status['resubmit']),
        'verified': len(candidate_data_by_status['verified']),
        'reqAttention': req_attention_count
    }

    return jsonify(monitor_data)
