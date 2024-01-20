"""Proctor Auth - Login View"""
from flask import flash, redirect, url_for, render_template
from flask_login import login_user
from proctor.auth.base import auth_bp
from proctor.auth.forms import LoginForm

@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    """Login Method."""
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('labs.index'))
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)
