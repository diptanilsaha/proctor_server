from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from proctor import db


class Role(db.Model):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)


    @staticmethod
    def insert_roles():
        roles = ['Administrator', 'Lab Moderator']
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                db.session.add(role)
            db.session.commit()

    def is_admin(self):
        return 'Administrator' == self.name

    def __repr__(self):
        return '<Role %r>' % self.name



class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(40), nullable=False)
    username: Mapped[str] = mapped_column(db.String(10), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates="users")

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

