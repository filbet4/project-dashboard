"""
Project routes for Phase 3.

These endpoints handle:
- POST /projects - Create a project
- GET /projects - List projects for the current user
- GET /projects/{project_id} - Get one project
- PUT /projects/{project_id} - Update a project
- DELETE /projects/{project_id} - Delete a project (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import ProjectMember, Document
from app.database import get_db
from app.models import User, Project, ProjectMember
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.dependencies import (
    get_current_user,
    get_project as get_project_or_404,
    require_owner,
    require_project_member,
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, token: str = None, db: Session = Depends(get_db)):
    """Create a new project owned by the current user."""
    current_user = get_current_user(token, db)

    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )

    # Save project first
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Automatically register the owner as the first project member
    owner_member = ProjectMember(
        project_id=new_project.id,
        user_id=current_user.id,
        role="OWNER"
    )

    db.add(owner_member)
    db.commit()

    return new_project


@router.get("", response_model=list[ProjectResponse])
def list_projects(token: str = None, db: Session = Depends(get_db)):
    """List projects owned by the current user."""
    current_user = get_current_user(token, db)

    memberships = (
        db.query(ProjectMember)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )

    project_ids = [m.project_id for m in memberships]

    projects = (
        db.query(Project)
        .filter(Project.id.in_(project_ids))
        .order_by(Project.created_at.desc())
        .all()
    )

    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    project_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)

    project = get_project_or_404(project_id, db)

    require_project_member(
        project.id,
        current_user,
        db
    )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_data: ProjectUpdate, token: str = None, db: Session = Depends(get_db)):
    """Update a project if the current user owns it."""
    current_user = get_current_user(token, db)
    project = get_project_or_404(project_id, db)
    require_project_member(
    project.id,
    current_user,
    db
    )

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Delete a project if the current user owns it."""

    current_user = get_current_user(token, db)

    project = get_project_or_404(project_id, db)

    require_owner(project, current_user)

    db.delete(project)
    db.commit()

    return {"detail": "Project deleted successfully"}