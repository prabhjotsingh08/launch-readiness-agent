import os
import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.linear import LinearProject, LinearIssue

logger = logging.getLogger(__name__)

class LinearClient:
    def __init__(self):
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.api_url = os.getenv("LINEAR_API_URL", "https://api.linear.app/graphql")
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY environment variable is not set")
        
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    async def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the Linear API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={"query": query, "variables": variables or {}}
            )
            response.raise_for_status()
            return response.json()

    async def get_projects(self) -> List[LinearProject]:
        """Fetch all projects from Linear"""
        query = """
        query {
            projects {
                nodes {
                    id
                    name
                    description
                    state
                    createdAt
                    updatedAt
                    targetDate
                    progress
                }
            }
        }
        """
        
        result = await self._execute_query(query)
        projects = []
        for node in result["data"]["projects"]["nodes"]:
            projects.append(
                LinearProject(
                    id=node["id"],
                    name=node["name"],
                    description=node["description"],
                    state=node["state"],
                    created_at=datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(node["updatedAt"].replace("Z", "+00:00")),
                    target_date=datetime.fromisoformat(node["targetDate"].replace("Z", "+00:00")) if node["targetDate"] else None,
                    progress=node["progress"]
                )
            )
        return projects

    async def get_project(self, project_id: str) -> Optional[LinearProject]:
        """Fetch a specific project from Linear"""
        query = """
        query($id: String!) {
            project(id: $id) {
                id
                name
                description
                state
                createdAt
                updatedAt
                targetDate
                progress
            }
        }
        """
        
        result = await self._execute_query(query, {"id": project_id})
        project_data = result["data"]["project"]
        if not project_data:
            return None
            
        return LinearProject(
            id=project_data["id"],
            name=project_data["name"],
            description=project_data["description"],
            state=project_data["state"],
            created_at=datetime.fromisoformat(project_data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(project_data["updatedAt"].replace("Z", "+00:00")),
            target_date=datetime.fromisoformat(project_data["targetDate"].replace("Z", "+00:00")) if project_data["targetDate"] else None,
            progress=project_data["progress"]
        )

    async def update_project(self, project_id: str, state: str, progress: Optional[float] = None, description: Optional[str] = None) -> LinearProject:
        """Update a project's status in Linear"""
        query = """
        mutation(
            $id: String!
            $state: String!
            $progress: Float
            $description: String
        ) {
            updateProject(
                id: $id
                input: {
                    state: $state
                    progress: $progress
                    description: $description
                }
            ) {
                project {
                    id
                    name
                    description
                    state
                    createdAt
                    updatedAt
                    targetDate
                    progress
                }
            }
        }
        """
        
        variables = {
            "id": project_id,
            "state": state,
            "progress": progress,
            "description": description
        }
        
        result = await self._execute_query(query, variables)
        project_data = result["data"]["updateProject"]["project"]
        
        return LinearProject(
            id=project_data["id"],
            name=project_data["name"],
            description=project_data["description"],
            state=project_data["state"],
            created_at=datetime.fromisoformat(project_data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(project_data["updatedAt"].replace("Z", "+00:00")),
            target_date=datetime.fromisoformat(project_data["targetDate"].replace("Z", "+00:00")) if project_data["targetDate"] else None,
            progress=project_data["progress"]
        )

    async def create_or_update_issue(self, title: str, description: str, project_id: Optional[str] = None) -> LinearIssue:
        """Create or update an issue in Linear"""
        query = """
        mutation(
            $title: String!
            $description: String!
            $projectId: String
        ) {
            createIssue(
                input: {
                    title: $title
                    description: $description
                    projectId: $projectId
                }
            ) {
                issue {
                    id
                    title
                    description
                    state
                    projectId
                    assigneeId
                    createdAt
                    updatedAt
                }
            }
        }
        """
        
        variables = {
            "title": title,
            "description": description,
            "projectId": project_id
        }
        
        result = await self._execute_query(query, variables)
        issue_data = result["data"]["createIssue"]["issue"]
        
        return LinearIssue(
            id=issue_data["id"],
            title=issue_data["title"],
            description=issue_data["description"],
            state=issue_data["state"],
            project_id=issue_data["projectId"],
            assignee_id=issue_data["assigneeId"],
            created_at=datetime.fromisoformat(issue_data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(issue_data["updatedAt"].replace("Z", "+00:00"))
        ) 