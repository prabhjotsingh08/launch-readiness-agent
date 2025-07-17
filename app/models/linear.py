from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class LinearProject(BaseModel):
    """Model representing a Linear project"""
    id: str
    name: str
    description: Optional[str] = None
    state: str
    created_at: datetime
    updated_at: datetime
    target_date: Optional[datetime] = None
    progress: Optional[float] = Field(None, ge=0, le=100)

class LinearIssue(BaseModel):
    """Model representing a Linear issue"""
    id: str
    title: str
    description: Optional[str] = None
    state: str
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProjectUpdateRequest(BaseModel):
    """Request model for updating project status"""
    project_id: str
    state: str
    progress: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    """Response model for project operations"""
    success: bool
    message: str
    data: Optional[LinearProject] = None

class ProjectListResponse(BaseModel):
    """Response model for listing projects"""
    success: bool
    message: str
    data: List[LinearProject] 