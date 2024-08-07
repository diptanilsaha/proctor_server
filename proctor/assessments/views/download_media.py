from flask import send_from_directory, current_app
from flask_login import login_required
from proctor.assessments.base import assess_bp

@assess_bp.route("/file/<filename>")
@login_required
def download_media(filename):
    flag = True
    if filename.split('.')[-1] == 'pdf':
        flag = False
    return send_from_directory(
        current_app.config['ASSESSMENT_MEDIA'],
        filename,
        as_attachment=flag
    )
