from flask import render_template
from proctor.candidate.base import candidate_bp

@candidate_bp.route('/')
def index():
    return render_template(
        "candidate/index.html",
        title="Candidate",
    )
