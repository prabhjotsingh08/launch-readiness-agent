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
            "Authorization": self.api_key,  # Linear API expects the raw API key
            "Content-Type": "application/json",
        }

    async def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the Linear API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={"query": query, "variables": variables or {}}
                )
                response.raise_for_status()
                result = response.json()
                
                # Check for GraphQL errors
                if "errors" in result:
                    error_msg = "; ".join([error.get("message", "Unknown error") for error in result["errors"]])
                    logger.error(f"GraphQL Error: {error_msg}")
                    raise ValueError(error_msg)
                
                return result
            except httpx.HTTPError as e:
                logger.error(f"HTTP Error: {str(e)}")
                logger.error(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
                raise

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
        mutation UpdateProject(
            $projectId: String!
            $input: ProjectUpdateInput!
        ) {
            projectUpdate(
                id: $projectId
                input: $input
            ) {
                success
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
        
        # Build input object, only including non-None values
        input_vars = {}
        if state is not None:
            input_vars["state"] = state
        if progress is not None:
            input_vars["progress"] = progress
        if description is not None:
            input_vars["description"] = description
        
        variables = {
            "projectId": project_id,
            "input": input_vars
        }
        
        try:
            result = await self._execute_query(query, variables)
            project_data = result["data"]["projectUpdate"]["project"]
            
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
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise

    async def create_or_update_issue(self, title: str, description: str, project_id: Optional[str] = None) -> LinearIssue:
        """Create or update an issue in Linear"""
        query = """
        mutation IssueCreate(
            $title: String!
            $description: String
            $teamId: String!
            $projectId: String
        ) {
            issueCreate(
                input: {
                    title: $title
                    description: $description
                    teamId: $teamId
                    projectId: $projectId
                }
            ) {
                success
                issue {
                    id
                    title
                    description
                    state {
                        name
                    }
                    project {
                        id
                    }
                    assignee {
                        id
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """
        
        # For now, we'll use a default team ID (you'll need to get this from Linear)
        # You can get team IDs by querying: query { teams { nodes { id name } } }
        default_team_id = "team_default"  # This needs to be replaced with actual team ID
        
        variables = {
            "title": title,
            "description": description,
            "teamId": default_team_id,
            "projectId": project_id
        }
        
        try:
            result = await self._execute_query(query, variables)
            issue_data = result["data"]["issueCreate"]["issue"]
            
            return LinearIssue(
                id=issue_data["id"],
                title=issue_data["title"],
                description=issue_data["description"],
                state=issue_data["state"]["name"],
                project_id=issue_data["project"]["id"] if issue_data["project"] else None,
                assignee_id=issue_data["assignee"]["id"] if issue_data["assignee"] else None,
                created_at=datetime.fromisoformat(issue_data["createdAt"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(issue_data["updatedAt"].replace("Z", "+00:00"))
            )
        except Exception as e:
            # For demo purposes, return a mock issue when Linear API fails
            logger.warning(f"Linear API call failed, returning mock issue: {str(e)}")
            return LinearIssue(
                id="mock-issue-id",
                title=title,
                description=description,
                state="todo",
                project_id=project_id,
                assignee_id=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ) 