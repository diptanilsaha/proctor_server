from typing import List
from flask_login import login_required, current_user
from flask import flash, redirect, url_for, render_template
from proctor.assessments.base import assess_bp
from proctor.assessments.forms import AssignCandidateForm
from proctor.models import (
    Client,
    Candidate,
    ClientSession,
    ClientSessionTimeline,
    ClientSessionTLStatus,
    CandidateStatus
)
from proctor.database import db

@assess_bp.route('/candidate/assign/<pk>/', methods=['GET', 'POST'])
@login_required
def assign(pk):
    candidate: Candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("Sorry, you don't have access.", "error")
            return redirect(url_for('assessments.index'))

    subq = db.select(Client).where(Client.lab_id == candidate.assessment.lab_id).subquery()
    active_client_sessions: List[ClientSession] = db.session.execute(
        db.select(ClientSession).join(subq, ClientSession.client_id == subq.c.id).where(
            ClientSession.is_active == True,
            ClientSession.candidate_id == None
        )
    ).scalars().all()

    client_session_choice = [('', "Select Client")]

    for client_session in active_client_sessions:
        client = client_session.client
        client_session_choice.append(
            client_session.id,
            f"{client.name} ({client.clientname})"
        )

    form = AssignCandidateForm()
    candidate_was_assigned = False
    if candidate.is_assigned:
        form = AssignCandidateForm(candidate)
        candidate_was_assigned = True

    form.client_session.choices = client_session_choice

    if form.validate_on_submit():
        client_session = db.session.get(ClientSession, form.client_session.data)

        client_session.candidate = candidate

        ctl = candidate.update_status(
            CandidateStatus.ASSIGNED,
            f"Candidate got assigned to {client_session.client.name}"
        )
        cl_status = ClientSessionTLStatus.CAA
        msg = f"{candidate.assessment.title}: {candidate.name} got assigned."
        if candidate_was_assigned:
            cl_status = ClientSessionTLStatus.CARA
            msg = f"{candidate.assessment.title}: {candidate.name} got re-assigned."

        cstl = ClientSessionTimeline(
            status = cl_status,
            details = msg,
            client_session = client_session
        )

        db.session.add_all([ctl, cstl])
        db.session.commit()
        flash_msg = "Candidate assigned successfully."
        if candidate_was_assigned:
            flash_msg = "Candidate re-assigned successfully."
        flash(flash_msg)
        return redirect(url_for("assessments.candidate_view", pk=candidate.id))

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, 'error')

    return render_template(
        "assessments/assign.html",
        title=f"Assign {candidate.roll} - {candidate.assessment.title}",
        form=form,
        candidate=candidate
    )
