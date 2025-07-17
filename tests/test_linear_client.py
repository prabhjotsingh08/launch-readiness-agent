import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.clients.linear import LinearClient
from app.models.linear import LinearProject, LinearIssue

@pytest.fixture
def mock_response():
    """Mock response data for Linear API"""
    return {
        "data": {
            "projects": {
                "nodes": [
                    {
                        "id": "proj-1",
                        "name": "Test Project",
                        "description": "A test project",
                        "state": "in_progress",
                        "createdAt": "2024-02-20T12:00:00Z",
                        "updatedAt": "2024-02-20T13:00:00Z",
                        "targetDate": "2024-03-20T00:00:00Z",
                        "progress": 50.0
                    }
                ]
            }
        }
    }

@pytest.fixture
def mock_project_response():
    """Mock response data for a single project"""
    return {
        "data": {
            "project": {
                "id": "proj-1",
                "name": "Test Project",
                "description": "A test project",
                "state": "in_progress",
                "createdAt": "2024-02-20T12:00:00Z",
                "updatedAt": "2024-02-20T13:00:00Z",
                "targetDate": "2024-03-20T00:00:00Z",
                "progress": 50.0
            }
        }
    }

@pytest.fixture
def mock_issue_response():
    """Mock response data for issue creation/update"""
    return {
        "data": {
            "createIssue": {
                "issue": {
                    "id": "issue-1",
                    "title": "Test Issue",
                    "description": "A test issue",
                    "state": "todo",
                    "projectId": "proj-1",
                    "assigneeId": None,
                    "createdAt": "2024-02-20T12:00:00Z",
                    "updatedAt": "2024-02-20T12:00:00Z"
                }
            }
        }
    }

@pytest.mark.asyncio
async def test_get_projects(mock_response):
    """Test fetching projects from Linear"""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = AsyncMock()
        
        client = LinearClient()
        projects = await client.get_projects()
        
        assert len(projects) == 1
        project = projects[0]
        assert isinstance(project, LinearProject)
        assert project.id == "proj-1"
        assert project.name == "Test Project"
        assert project.state == "in_progress"
        assert project.progress == 50.0

@pytest.mark.asyncio
async def test_get_project(mock_project_response):
    """Test fetching a single project from Linear"""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_project_response
        mock_post.return_value.raise_for_status = AsyncMock()
        
        client = LinearClient()
        project = await client.get_project("proj-1")
        
        assert project is not None
        assert isinstance(project, LinearProject)
        assert project.id == "proj-1"
        assert project.name == "Test Project"
        assert project.state == "in_progress"
        assert project.progress == 50.0

@pytest.mark.asyncio
async def test_create_issue(mock_issue_response):
    """Test creating an issue in Linear"""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_issue_response
        mock_post.return_value.raise_for_status = AsyncMock()
        
        client = LinearClient()
        issue = await client.create_or_update_issue(
            title="Test Issue",
            description="A test issue",
            project_id="proj-1"
        )
        
        assert issue is not None
        assert isinstance(issue, LinearIssue)
        assert issue.id == "issue-1"
        assert issue.title == "Test Issue"
        assert issue.state == "todo"
        assert issue.project_id == "proj-1"

@pytest.mark.asyncio
async def test_linear_client_initialization():
    """Test Linear client initialization with missing API key"""
    with patch.dict("os.environ", clear=True):
        with pytest.raises(ValueError):
            LinearClient() 