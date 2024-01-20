"Proctor - Labs Index View."
from flask_login import login_required
from flask import render_template

from proctor.database import db
from proctor.labs.base import labs_bp
from proctor.models import Lab
from proctor.decorators import admin_required

@labs_bp.route('/')
@login_required
@admin_required
def index():
    """Labs - Index."""
    labs = db.session.execute(db.select(Lab)).all()
    return render_template(
        "lab/index.html",
        labs=labs
    )
