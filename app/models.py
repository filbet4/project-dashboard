"""
SQLAlchemy ORM models.

"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    projects = relationship(
    "Project",
    back_populates="owner"
    )

    memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)

    description = Column(Text, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    owner = relationship(
        "User",
        back_populates="projects"
    )

    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"

class Document(Base):
    """
    Document table - stores uploaded files for projects.

    Attributes:
        id: Unique identifier
        filename: Original filename uploaded by the user
        filepath: Physical path on disk
        content_type: MIME type (application/pdf, etc.)
        project_id: Project that owns the document
        uploaded_at: Upload timestamp
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    filepath = Column(String, nullable=False)

    content_type = Column(String, nullable=False)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    def __repr__(self):
        return (
            f"<Document(id={self.id}, "
            f"filename={self.filename}, "
            f"project_id={self.project_id})>"
        )
    project = relationship(
    "Project",
    back_populates="documents"
    )
    
class ProjectMember(Base):
    """
    Stores users participating in projects.

    A project always has:
        - one OWNER
        - zero or more PARTICIPANTS
    """

    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    role = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member"
        ),
    )

    def __repr__(self):
        return (
            f"<ProjectMember("
            f"project={self.project_id}, "
            f"user={self.user_id}, "
            f"role={self.role})>"
        )
    project = relationship(
    "Project",
    back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="memberships"
    )
        