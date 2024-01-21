"""Proctor Auth - Logout View"""
from flask import redirect, url_for
from flask_login import login_required, logout_user
from proctor.auth.base import auth_bp

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout User."""
    logout_user()
    return redirect('/')
