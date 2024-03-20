"""Proctor Config"""
import os
from dotenv import load_dotenv
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from .jobs import expire_assessments_job

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(ROOT_DIR, 'proctor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASSESSMENT_MEDIA = os.path.join(ROOT_DIR, 'assessment_media')
    SUBMISSION_MEDIA = os.path.join(ROOT_DIR, 'submission_media')
    JOBS = [{
        "id": "expire_assessment",
        "replace_existing": True,
        "func": expire_assessments_job,
        "trigger": "interval",
        "seconds": 60
    }]
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///flask_context.db")
    }
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
