from typing import List
from flask_login import login_required, current_user
from flask import flash, redirect, url_for, render_template
from proctor.assessments.base import assess_bp
from proctor.assessments.forms import AssignCandidateForm
from proctor.models import (
    AssessmentStatus,
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
    """Assign/Re-assign Candidates to Active Client Session."""
    candidate: Candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("Sorry, you don't have access.", "error")
            return redirect(url_for('assessments.index'))

    if candidate.assessment.current_status not in [
        AssessmentStatus.ACTIVE,
        AssessmentStatus.REG,
    ]:
        flash("Candidates can be assigned only if Assessment is in \
              'Registration' or 'Active' Phase.", "error")
        return redirect(url_for('assessments.candidate_view', pk=candidate.id))

    subq = db.select(Client).where(Client.lab_id == candidate.assessment.lab_id).subquery()
    active_client_sessions: List[ClientSession] = db.session.execute(
        db.select(ClientSession).join(subq, ClientSession.client_id == subq.c.id).where(
            ClientSession.is_active == True,
            ClientSession.candidate_id == None,
            ClientSession.can_terminate == False
        )
    ).scalars().all()

    client_session_choice = [('', "Select Client")]

    for client_session in active_client_sessions:
        client = client_session.client
        client_session_choice.append((
            client_session.id,
            f"{client.name} ({client.clientname})"
        ))

    form = AssignCandidateForm()
    candidate_was_assigned = False
    if candidate.is_assigned:
        form = AssignCandidateForm(obj=candidate)
        candidate_was_assigned = True

    form.client_session.choices = client_session_choice

    if form.validate_on_submit():
        client_session = db.session.get(ClientSession, form.client_session.data)

        client_session.candidate = candidate

        cl_status = ClientSessionTLStatus.CAA
        msg = f"{candidate.assessment.title}: {candidate.name} got assigned."
        ctl_msg = f"Candidate got assigned to {client_session.client.name}"

        db_models_objects = []

        if candidate_was_assigned:
            # Reassigning message
            cl_status = ClientSessionTLStatus.CARA
            msg = f"{candidate.assessment.title}: {candidate.name} got re-assigned."
            ctl_msg = f"Candidate got reassigned to {client_session.client.name}"

            # freeing previous assigned client if previous client session is active
            if candidate.client_session.is_active:
                free_cl_status = ClientSessionTLStatus.CAFREE
                free_cl_message = f"{candidate.assessment.title}: {candidate.name} got reassigned."
                free_cl = ClientSessionTimeline(
                    status = free_cl_status,
                    details = free_cl_message,
                    client_session = candidate.client_session
                )
                candidate.client_session.candidate = None
                db_models_objects.append(free_cl)

        if candidate.current_status == CandidateStatus.WAITING:
            ctl = candidate.update_status(
                CandidateStatus.ASSIGNED,
                ctl_msg
            )
            db_models_objects.append(ctl)

        if candidate.assessment.current_status == AssessmentStatus.ACTIVE \
            and candidate.current_status == CandidateStatus.ASSIGNED:
            pending_ctl = candidate.update_status(
                CandidateStatus.PENDING,
                "Candidate submission is pending."
            )
            db_models_objects.append(pending_ctl)


        cstl = ClientSessionTimeline(
            status = cl_status,
            details = msg,
            client_session = client_session
        )

        db_models_objects.append(cstl)

        db.session.add_all(db_models_objects)
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


@assess_bp.route('/candidate/remove/<pk>/', methods=['POST'])
@login_required
def remove(pk):
    """Remove assigned Client Sessions from assigned Candidates."""
    candidate: Candidate = db.get_or_404(Candidate, pk)

    if not current_user.is_admin:
        if current_user.lab != candidate.assessment.lab:
            flash("Sorry, you don't have access.", "error")
            return redirect(url_for('assessments.index'))

    if candidate.assessment.current_status not in [
        AssessmentStatus.REG,
    ]:
        flash("Client Sessions can be removed from assigned candidates\
              during 'Initial' or 'Registration' phase.", "error")
        return redirect(url_for('assessments.candidate_view', pk=candidate.id))


    client_session = candidate.client_session
    client_session.candidate = None

    ctl = candidate.update_status(
        CandidateStatus.WAITING,
        f"Candidate removed from {client_session.client.name}"
    )

    cstl = ClientSessionTimeline(
        status = ClientSessionTLStatus.CAFREE,
        details = f"{candidate.assessment.title}: {candidate.name} removed.",
        client_session = client_session
    )

    db.session.add_all([ctl, cstl])
    db.session.commit()

    flash("Candidate removed from the assigned Client Session.")
    return redirect(url_for("assessments.candidate_view", pk=candidate.id))
