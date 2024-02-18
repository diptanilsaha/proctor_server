"""Proctor Models."""
import uuid
import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import ForeignKey, func, UniqueConstraint, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing_extensions import Annotated
from .database import db
from .utils import generate_clientname, calculate_duration


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
    ROBOT = 'Robot'


class Role(db.Model):
    """Role Model."""
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(12), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    @staticmethod
    def insert_roles():
        """Inserts 'Administrator' and 'Lab Moderator' role if doesn't exists on DB."""
        roles = [RoleName.ADMIN, RoleName.LAB_MOD, RoleName.ROBOT]
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                db.session.add(role)
            db.session.commit()

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    """User Model."""
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        db.String(10), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates="users")
    lab_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped[Optional["Lab"]] = relationship(back_populates="user")
    clients_created: Mapped[List["Client"]] = relationship(
        back_populates="created_by")
    cs_tl_attended: Mapped[List["ClientSessionTimeline"]] = relationship(
        back_populates="attended_by"
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        back_populates="created_by")
    assessment_tl: Mapped[List["AssessmentTimeline"]
                          ] = relationship(back_populates="atl_created_by")
    cs_verifier: Mapped[List["Candidate"]] = relationship(
        back_populates="sub_verified_by")
    created_at: Mapped[TimeStamp]

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Hash and sets password with a string."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Checks and matches password with a string."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return RoleName.ADMIN == self.role.name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Lab(db.Model):
    """Lab Model."""
    __tablename__ = "lab"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    labname: Mapped[str] = mapped_column(
        db.String(40), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="lab")
    clients: Mapped[List["Client"]] = relationship(back_populates="lab")
    assessments: Mapped[List["Assessment"]] = relationship(
        back_populates="lab",
        cascade="all, delete-orphan"
    )
    created_at: Mapped[TimeStamp]

    def __repr__(self):
        return f"<Lab {self.labname}>"


class Client(db.Model):
    """Client Model."""
    __tablename__ = "client"
    id: Mapped[str] = mapped_column(
        db.String(32), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(db.String(40), nullable=False)
    clientname: Mapped[str] = mapped_column(
        db.String(40), nullable=False, default=generate_clientname
    )
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="clients")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(back_populates="clients_created")
    created_at: Mapped[TimeStamp]
    is_registered: Mapped[bool] = mapped_column(db.Boolean, default=False)
    registered_at: Mapped[datetime.datetime] = mapped_column(
        db.DateTime, nullable=True, server_default=func.CURRENT_TIMESTAMP())
    client_sessions: Mapped[List["ClientSession"]] = relationship(
        back_populates="client",
        order_by=desc("session_start_time"),
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("clientname", "lab_id", name="clientname_lab_uidx"),
    )

    def __repr__(self):
        return f"<Client f{self.clientname}>"

    @property
    def is_active(self):
        if self.client_sessions and self.client_sessions[0].is_active:
            return True
        return False


class ClientSession(db.Model):
    """ClientSession Model."""
    __tablename__ = "clientSession"
    id: Mapped[str] = mapped_column(
        db.String(32),
        primary_key=True,
        default=generate_uuid)
    session_ip_addr: Mapped[str] = mapped_column(db.String(15), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=True)
    can_terminate: Mapped[bool] = mapped_column(
        db.Boolean, nullable=False, default=False)
    session_start_time: Mapped[TimeStamp]
    session_end_time: Mapped[datetime.datetime] = mapped_column(
        db.DateTime, nullable=True, server_default=func.CURRENT_TIMESTAMP())
    session_timeline: Mapped[List["ClientSessionTimeline"]] = relationship(
        back_populates="client_session", cascade="all, delete-orphan")
    client_id: Mapped[str] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="client_sessions")
    candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("candidate.id"), nullable=True)
    candidate: Mapped[Optional["Candidate"]] = relationship(
        back_populates="client_sessions")

    def __repr__(self):
        return f"<ClientSession {self.id} of {self.client}>"


class ClientSessionTLStatus(Enum):
    """ClientSession Timeline Status"""
    CC = "Client Connected"
    UC = "USB Device Connected"
    UD = "USB Device Disconnected"
    CAA = "Candidate Assigned"
    CALI = "Candidate Logged In"
    CALO = "Candidate Logged Out"
    CAFREE = "Candidate Removed From Client"
    CARA = "Candidate Re-Assigned"
    TR = "Termination Requested"
    CDWOTR = "Client Disconnected before Terminate Request"
    CDWRT = "Client Disconnected after Terminate Request"


class ClientSessionTimeline(db.Model):
    """ClientSessionTimeline Model."""
    __tablename__ = "clientSessionTimeline"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    status: Mapped[ClientSessionTLStatus]
    requires_attention: Mapped[bool] = mapped_column(db.Boolean, default=False)
    details: Mapped[str] = mapped_column(db.Text, nullable=False)
    client_session_id: Mapped[str] = mapped_column(
        ForeignKey("clientSession.id"))
    client_session: Mapped["ClientSession"] = relationship(
        back_populates="session_timeline")
    attended_by_id: Mapped[Optional[int]
                           ] = mapped_column(ForeignKey("user.id"))
    attended_by: Mapped[Optional["User"]] = relationship(
        back_populates="cs_tl_attended")
    timestamp: Mapped[TimeStamp]


class AssessmentStatus(Enum):
    """Assessment Status Enum."""
    INIT = "initial"
    REG = "registration"
    ACTIVE = "active"
    BUFFER = "buffer"
    COMPLETE = "complete"
    EXPIRED = "expire"


class Assessment(db.Model):
    """Assessment Model."""
    __tablename__ = "assessment"
    id: Mapped[str] = mapped_column(
        db.String(32),
        primary_key=True,
        default=generate_uuid
    )
    title: Mapped[str] = mapped_column(db.String(50), nullable=False)
    description: Mapped[str] = mapped_column(db.Text)
    media: Mapped[str] = mapped_column(db.String(32))
    current_status: Mapped[AssessmentStatus] = mapped_column(
        default=AssessmentStatus.INIT
    )
    created_at: Mapped[TimeStamp]
    lab_id: Mapped[int] = mapped_column(ForeignKey("lab.id"))
    lab: Mapped["Lab"] = relationship(back_populates="assessments")
    start_time: Mapped[datetime.datetime] = mapped_column(db.DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(db.DateTime)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(back_populates="assessments")
    candidates: Mapped[List["Candidate"]] = relationship(
        back_populates="assessment",
        order_by="Candidate.roll",
        cascade="all, delete-orphan"
    )
    assessment_timeline: Mapped[List["AssessmentTimeline"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by=desc("timestamp")
    )

    def __repr__(self):
        return f"<Assessment {self.title}>"

    @property
    def duration(self):
        return calculate_duration(self.start_time, self.end_time)

    @staticmethod
    def insert_assessment(
        title: str,
        description: str,
        media: str,
        lab_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        user: User
    ):
        assessment = Assessment(
            title = title,
            description = description,
            media = media,
            lab_id = lab_id,
            start_time = start_time,
            end_time = end_time,
            created_by = user
        )
        atl = AssessmentTimeline(
            status = AssessmentStatus.INIT,
            atl_created_by = user,
            assessment = assessment
        )
        db.session.add_all([assessment, atl])
        db.session.commit()
        return assessment



class AssessmentTimeline(db.Model):
    """Assessment Timline Model."""
    __tablename__ = "assessmentTimeLine"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    status: Mapped[AssessmentStatus]
    timestamp: Mapped[TimeStamp]
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessment.id"))
    assessment: Mapped["Assessment"] = relationship(
        back_populates="assessment_timeline")
    atl_created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    atl_created_by: Mapped["User"] = relationship(
        back_populates="assessment_tl")


class CandidateStatus(Enum):
    """
    Candidate Status Enum.

    WAITING - Candidate created and waiting for Assignment.
    ASSIGNED - Candidate is assigned to a Client, waiting for Assessment Activation.
    PENDING - Assessment is activated and Candidate submission is pending.
    SUBMITTED - Candidate has submitted some work.
    RESUBMIT - Candidate's work has been rejected and need to Resubmit his work.
    VERIFIED - Candidate's work has been accepted. He/she can leave the client.
    """
    WAITING = "waiting"
    ASSIGNED = "assigned"
    PENDING = "pending"
    SUBMITTED = "submitted"
    RESUBMIT = "resubmit"
    VERIFIED = "verified"


class Candidate(db.Model):
    """Candidate Model."""
    __tablename__ = "candidate"
    id: Mapped[str] = mapped_column(
        db.String(32),
        primary_key=True,
        default=generate_uuid,
    )
    name: Mapped[str] = mapped_column(db.String(40))
    roll: Mapped[str] = mapped_column(db.String(20))
    submission_media_url: Mapped[str] = mapped_column(db.String(50), nullable=True)
    current_status: Mapped[CandidateStatus] = mapped_column(
        default=CandidateStatus.WAITING
    )
    sub_verified_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    sub_verified_by: Mapped["User"] = relationship(
        back_populates="cs_verifier")
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessment.id"))
    assessment: Mapped["Assessment"] = relationship(
        back_populates="candidates")
    client_sessions: Mapped[List["ClientSession"]] = relationship(
        back_populates="candidate",
        order_by=desc("session_start_time")
    )
    timeline: Mapped[List["CandidateTimeline"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("roll", "assessment_id", name="assessment_roll_uidx"),
    )

    @staticmethod
    def insert_candidate(name: str, roll: str, assessment: Assessment):
        candidate = Candidate(
            name = name,
            roll = roll,
            assessment = assessment
        )
        ctl = CandidateTimeline(
            status = CandidateStatus.WAITING,
            candidate = candidate
        )
        db.session.add_all([candidate, ctl])
        db.session.commit()

    def __repr__(self):
        return f"<Candidate {self.assessment.title} {self.name}>"

    @property
    def is_assigned(self):
        return bool(self.client_sessions)

    @property
    def client_session(self) -> ClientSession:
        if self.client_sessions:
            return self.client_sessions[0]

    def update_status(self, status: CandidateStatus, details: str = None):
        self.current_status = status
        tl = CandidateTimeline(
            candidate_id = self.id,
            status = status
        )
        if details:
            tl.details = details
        return tl


class CandidateTimeline(db.Model):
    """Candidate Timeline Model."""
    __tablename__ = "candidateTimeline"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    status: Mapped[CandidateStatus]
    details: Mapped[str] = mapped_column(db.Text, nullable=True)
    timestamp: Mapped[TimeStamp]
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidate.id"))
    candidate: Mapped["Candidate"] = relationship(back_populates="timeline")
