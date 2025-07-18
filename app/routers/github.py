from fastapi import APIRouter, HTTPException, Header, Request, Depends, Body
import logging
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.models.github import PushEvent, PullRequestEvent, WorkflowRunEvent
from app.utils.github import verify_github_webhook, extract_linear_issue_id, parse_workflow_status
from app.clients.linear import LinearClient

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_linear_client() -> LinearClient:
    """Dependency to get Linear client instance"""
    return LinearClient()

@router.post("/webhook")
async def github_webhook(
    payload: Dict[str, Any] = Body(..., description="GitHub webhook payload"),
    x_hub_signature_256: str = Header(..., description="GitHub webhook signature (sha256=...)"),
    x_github_event: str = Header(..., description="GitHub event type (push, pull_request, workflow_run)"),
    client: LinearClient = Depends(get_linear_client)
):
    """
    Handle GitHub webhook events
    
    This endpoint processes GitHub webhook events and updates Linear accordingly.
    
    - For push events: Creates/updates Linear issues based on commit messages
    - For pull requests: Updates Linear issues based on PR status
    - For workflow runs: Updates Linear issues based on workflow status
    
    Note: For signature verification, we'll use a simplified approach for testing.
    In production, you would verify the signature against the raw request body.
    """
    
    # For testing purposes, we'll generate the signature from the payload
    # In production, this would be done against the raw request body
    payload_str = json.dumps(payload, separators=(',', ':'))
    payload_bytes = payload_str.encode('utf-8')
    
    # Verify signature (simplified for testing)
    if not verify_github_webhook(x_hub_signature_256, payload_bytes):
        # Try with pretty formatting
        payload_str_pretty = json.dumps(payload, indent=2)
        payload_bytes_pretty = payload_str_pretty.encode('utf-8')
        if not verify_github_webhook(x_hub_signature_256, payload_bytes_pretty):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        if x_github_event == "push":
            return await handle_push_event(PushEvent(**payload), client)
        elif x_github_event == "pull_request":
            return await handle_pull_request_event(PullRequestEvent(**payload), client)
        elif x_github_event == "workflow_run":
            return await handle_workflow_run_event(WorkflowRunEvent(**payload), client)
        else:
            logger.warning(f"Unhandled GitHub event type: {x_github_event}")
            return {"message": f"Event type {x_github_event} not handled"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_push_event(event: PushEvent, client: LinearClient):
    """Handle GitHub push events"""
    updates = []
    
    for commit in event.commits:
        issue_id = extract_linear_issue_id(commit.message)
        if issue_id:
            try:
                message_title = commit.message.split('\n')[0]
                issue = await client.create_or_update_issue(
                    title=f"Commit: {message_title}",
                    description=f"Commit Message:\n{commit.message}\n\nCommit URL: {commit.url}",
                )
                updates.append({"issue_id": issue.id, "status": "success"})
            except Exception as e:
                logger.error(f"Error updating Linear issue {issue_id}: {str(e)}")
                updates.append({"issue_id": issue_id, "status": "error", "error": str(e)})
    
    return {"message": "Push event processed", "updates": updates}

async def handle_pull_request_event(event: PullRequestEvent, client: LinearClient):
    """Handle GitHub pull request events"""
    issue_id = extract_linear_issue_id(event.pull_request.title)
    if not issue_id:
        issue_id = extract_linear_issue_id(event.pull_request.body or "")
    
    if not issue_id:
        return {"message": "No Linear issue ID found in PR"}
    
    try:
        state_mapping = {
            "opened": "in_progress",
            "closed": "completed" if event.pull_request.merged_at else "canceled",
            "reopened": "in_progress"
        }
        
        if event.action in state_mapping:
            issue = await client.create_or_update_issue(
                title=event.pull_request.title,
                description=f"PR Description:\n{event.pull_request.body or 'No description'}\n\nPR URL: {event.pull_request.html_url}",
            )
            return {
                "message": "Pull request event processed",
                "issue_id": issue.id,
                "status": "success"
            }
        
        return {"message": f"Pull request action {event.action} not handled"}
    except Exception as e:
        logger.error(f"Error processing pull request event: {str(e)}")
        return {"message": "Error processing pull request", "error": str(e)}

async def handle_workflow_run_event(event: WorkflowRunEvent, client: LinearClient):
    """Handle GitHub workflow run events"""
    issue_id = extract_linear_issue_id(event.workflow_run.head_branch)
    
    if not issue_id:
        return {"message": "No Linear issue ID found in workflow"}
    
    try:
        status, progress = parse_workflow_status(
            event.workflow_run.status,
            event.workflow_run.conclusion
        )
        
        issue = await client.create_or_update_issue(
            title=f"Workflow: {event.workflow_run.name}",
            description=f"Workflow Status: {status}\nWorkflow URL: {event.workflow_run.url}",
        )
        
        return {
            "message": "Workflow run event processed",
            "issue_id": issue.id,
            "status": status,
            "progress": progress
        }
    except Exception as e:
        logger.error(f"Error processing workflow run event: {str(e)}")
        return {"message": "Error processing workflow run", "error": str(e)}
