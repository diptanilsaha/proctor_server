"""Proctor Models."""

import uuid
import datetime
from enum import Enum
from typing import List
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing_extensions import Annotated
from proctor import db


TimeStamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]

def generate_uuid():
    """Returns UUID as a 32-character lowercase hexadecimal string"""
    return uuid.uuid4().hex

class RoleName:
    """RoleName"""
    ADMIN = 'Administrator'
    LAB_MOD = 'Lab Moderator'



class Role(db.Model):
    """Role Model."""
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    @staticmethod
    def insert_roles():
        """Inserts 'Administrator' and 'Lab Moderator' role if doesn't exists on DB."""
        roles = [RoleName.ADMIN, RoleName.LAB_MOD]
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                db.session.add(role)
            db.session.commit()

    def is_admin(self):
        """Checks if Role is 'Administrator' or not."""
        return RoleName.ADMIN == self.name

    def __repr__(self):
        return f"<Role {self.name}>"



class User(UserMixin, db.Model):
    """User Model."""
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(10), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates="users")
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="user")
    clients_created: Mapped[List["Client"]] = relationship(back_populates="created_by")
    created_at: Mapped[TimeStamp]

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Hash and sets password with a string."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks and matches password with a string."""
        return check_password_hash(self.password_hash, password)



class Lab(db.Model):
    """Lab Model."""
    __tablename__ = "lab"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    labname: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="lab")
    clients: Mapped[List["Client"]] = relationship(back_populates="lab")
    created_at: Mapped[TimeStamp]

    def __repr__(self):
        return f"<Lab {self.labname}>"



class Client(db.Model):
    """Client Model."""
    __tablename__ = "client"
    id: Mapped[str] = mapped_column(db.String(32), primary_key=True, default=generate_uuid)
    clientname: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="clients")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(back_populates="clients_created")
    created_at: Mapped[TimeStamp]
    client_sessions: Mapped[List["ClientSession"]] = relationship(back_populates="client")

    def __repr__(self):
        return f"<Client f{self.clientname}>"



class ClientSession(db.Model):
    """ClientSession Model."""
    __tablename__ = "clientSession"
    id: Mapped[str] = mapped_column(db.String(32), primary_key=True, default=generate_uuid)
    session_ip_addr: Mapped[str] = mapped_column(db.String(15), nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    can_terminate: Mapped[bool] = mapped_column(db.Booelan, nullable=False, default=False)
    session_start_time: Mapped[TimeStamp]
    session_end_time: Mapped[datetime.datetime] = mapped_column(db.DateTime, nullable=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="client_sessions")

    def __repr__(self):
        return f"<ClientSession {self.id} of {self.client}>"
