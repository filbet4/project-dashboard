"""
Shared dependencies used across the application.

Keeping authentication and authorization logic
in one place avoids code duplication.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.models import User, Project, ProjectMember


def get_current_user(token: str, db: Session) -> User:
    """
    Returns the authenticated user based on JWT token.
    """

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )

    token = token.strip('"').strip("'")

    payload = decode_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.id == int(payload["sub"]))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def get_project(project_id: int, db: Session) -> Project:
    """
    Returns a project or raises 404.
    """

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


def require_owner(project: Project, user: User):
    """
    Allows access only to the project owner.
    """

    if project.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action"
        )


def require_project_member(project_id: int, user: User, db: Session):
    """
    Allows access to every project member
    (OWNER and PARTICIPANT).
    """

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )

    return member