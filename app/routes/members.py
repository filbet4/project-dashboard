"""
Project member routes.

Handles:
- Invite users
- List project members
- Remove participants
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ProjectMember

from app.schemas import (
    MemberInvite,
    MemberResponse
)

from app.dependencies import (
    get_current_user,
    get_project,
    require_owner,
)

router = APIRouter(
    prefix="/projects",
    tags=["members"]
)

@router.post(
    "/{project_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED
)
def invite_member(
    project_id: int,
    invite: MemberInvite,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Invite a user to collaborate on a project.

    Only the OWNER can invite new members.
    """

    current_user = get_current_user(token, db)

    project = get_project(project_id, db)

    require_owner(
        project,
        current_user
    )

    invited_user = (
        db.query(User)
        .filter(User.email == invite.email)
        .first()
    )

    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == invited_user.id
        )
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )

    member = ProjectMember(
        project_id=project.id,
        user_id=invited_user.id,
        role="PARTICIPANT"
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member

@router.get(
    "/{project_id}/members",
    response_model=list[MemberResponse]
)
def list_members(
    project_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    List all members of a project.

    Only the OWNER can view the member list.
    """

    current_user = get_current_user(token, db)

    project = get_project(project_id, db)

    require_owner(
        project,
        current_user
    )

    members = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id)
        .order_by(ProjectMember.created_at.asc())
        .all()
    )

    return members


@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Remove a participant from a project.

    Only the OWNER can remove members.
    The OWNER cannot remove themselves.
    """

    current_user = get_current_user(token, db)

    project = get_project(project_id, db)

    require_owner(
        project,
        current_user
    )

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user_id
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    if member.role == "OWNER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project owner cannot be removed"
        )

    db.delete(member)
    db.commit()

    return {
        "detail": "Member removed successfully"
    }
