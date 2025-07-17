from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.linear import (
    LinearProject,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse
)
from app.clients.linear import LinearClient

router = APIRouter()

async def get_linear_client() -> LinearClient:
    """Dependency to get Linear client instance"""
    return LinearClient()

@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(client: LinearClient = Depends(get_linear_client)):
    """List all projects from Linear"""
    try:
        projects = await client.get_projects()
        return ProjectListResponse(
            success=True,
            message="Projects retrieved successfully",
            data=projects
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    client: LinearClient = Depends(get_linear_client)
):
    """Get a specific project from Linear"""
    try:
        project = await client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(
            success=True,
            message="Project retrieved successfully",
            data=project
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    update_data: ProjectUpdateRequest,
    client: LinearClient = Depends(get_linear_client)
):
    """Update a project's status in Linear"""
    try:
        project = await client.update_project(
            project_id=project_id,
            state=update_data.state,
            progress=update_data.progress,
            description=update_data.description
        )
        
        return ProjectResponse(
            success=True,
            message="Project updated successfully",
            data=project
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 