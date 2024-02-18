"""Proctor Flask extensions."""
from flask_login import LoginManager
from flask_apscheduler import APScheduler

login_manager = LoginManager()
login_manager.session_protection = "strong"

scheduler = APScheduler()
