"""Proctor Flask extensions."""
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = "strong"
