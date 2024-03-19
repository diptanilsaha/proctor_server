from flask import render_template
from flask_login import login_required, current_user
from proctor.monitor.base import monitor_bp
from proctor.assessments.utils import (
    _get_all_active_assessments,
    _get_active_assessments_by_lab
)

@monitor_bp.route('/')
@login_required
def index():
    assessments = _get_all_active_assessments()

    if not current_user.is_admin:
        assessments = _get_active_assessments_by_lab(current_user.lab)

    return render_template(
        "monitor/index.html",
        title="Monitor Live Assessments",
        assessments=assessments
    )
