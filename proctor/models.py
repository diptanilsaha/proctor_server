from typing import List
from sqlalchemy import ForeignKey, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from proctor import db
import datetime
from typing_extensions import Annotated

timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]

class UserType:
    ADMIN = 'Administrator'
    LAB_MOD = 'Lab Moderator'



class Role(db.Model):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)


    @staticmethod
    def insert_roles():
        roles = [UserType.ADMIN, UserType.LAB_MOD]
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                db.session.add(role)
            db.session.commit()

    def is_admin(self):
        return UserType.ADMIN == self.name

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
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="user")
    clients_created: Mapped[List["Client"]] = relationship(back_populates="created_by")
    created_at: Mapped[timestamp]

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Lab(db.Model):
    __tablename__ = "lab"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    labname: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="lab")
    clients: Mapped[List["Client"]] = relationship(back_populates="lab")
    created_at: Mapped[timestamp]

    def __repr__(self):
        return '<Lab %r>' % self.labname



class Client(db.Model):
    __tablename__ = "client"
    id: Mapped[str] = mapped_column(db.String(32), Uuid, primary_key=True)
    clientname: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="clients")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(back_populates="clients_created")
    created_at: Mapped[timestamp]
