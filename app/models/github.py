from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GitHubUser(BaseModel):
    """Model representing a GitHub user"""
    login: str
    id: int
    type: str

class GitHubRepository(BaseModel):
    """Model representing a GitHub repository"""
    id: int
    name: str
    full_name: str
    private: bool
    owner: GitHubUser

class GitHubCommit(BaseModel):
    """Model representing a GitHub commit"""
    id: str
    message: str
    timestamp: datetime
    author: GitHubUser
    url: str

class WorkflowRun(BaseModel):
    """Model representing a GitHub workflow run"""
    id: int
    name: str
    status: str
    conclusion: Optional[str]
    workflow_id: int
    head_branch: str
    head_sha: str
    run_number: int
    event: str
    url: str
    created_at: datetime
    updated_at: datetime

class PullRequest(BaseModel):
    """Model representing a GitHub pull request"""
    id: int
    number: int
    state: str
    title: str
    body: Optional[str]
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime]
    head: Dict[str, Any]
    base: Dict[str, Any]

class WebhookPayload(BaseModel):
    """Base model for GitHub webhook payloads"""
    action: Optional[str]
    repository: GitHubRepository
    sender: GitHubUser

class PushEvent(WebhookPayload):
    """Model for push events"""
    ref: str
    before: str
    after: str
    commits: List[GitHubCommit]

class PullRequestEvent(WebhookPayload):
    """Model for pull request events"""
    pull_request: PullRequest

class WorkflowRunEvent(WebhookPayload):
    """Model for workflow run events"""
    workflow_run: WorkflowRun 