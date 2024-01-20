"""Proctor Config"""
import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(ROOT_DIR, 'proctor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
