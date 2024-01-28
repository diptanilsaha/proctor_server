"""Proctor Auth Forms."""
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import StringField, PasswordField
from proctor.database import db
from proctor.models import User

class LoginForm(FlaskForm):
    """Proctor Login Form."""
    username = StringField('username', validators=[validators.InputRequired()])
    password = PasswordField('password', validators=[validators.InputRequired()])

    def get_user(self):
        """Return User from the given Username."""
        return db.session.execute(
            db.select(User).filter_by(username=self.username.data)
        ).scalar_one_or_none()
