import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'config.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
