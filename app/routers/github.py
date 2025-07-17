from fastapi import APIRouter, HTTPException, Header, Request, Depends
import logging
from typing import Optional

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
    request: Request,
    x_hub_signature_256: str = Header(...),
    x_github_event: str = Header(...),
    client: LinearClient = Depends(get_linear_client)
):
    """Handle GitHub webhook events"""
    # Get raw payload for signature verification
    payload_bytes = await request.body()
    
    # Verify webhook signature
    if not verify_github_webhook(x_hub_signature_256, payload_bytes):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload based on event type
    payload_json = await request.json()
    
    try:
        if x_github_event == "push":
            return await handle_push_event(PushEvent(**payload_json), client)
        elif x_github_event == "pull_request":
            return await handle_pull_request_event(PullRequestEvent(**payload_json), client)
        elif x_github_event == "workflow_run":
            return await handle_workflow_run_event(WorkflowRunEvent(**payload_json), client)
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
                issue = await client.create_or_update_issue(
                    title=f"Commit: {commit.message.split('\n')[0]}",
                    description=f"Commit Message:\n{commit.message}\n\nCommit URL: {commit.url}",
                )
                updates.append({"issue_id": issue.id, "status": "success"})
            except Exception as e:
                logger.error(f"Error updating Linear issue {issue_id}: {str(e)}")
                updates.append({"issue_id": issue_id, "status": "error", "error": str(e)})
    
    return {"message": "Push event processed", "updates": updates}

async def handle_pull_request_event(event: PullRequestEvent, client: LinearClient):
    """Handle GitHub pull request events"""
    # Extract Linear issue ID from PR title or body
    issue_id = extract_linear_issue_id(event.pull_request.title)
    if not issue_id:
        issue_id = extract_linear_issue_id(event.pull_request.body or "")
    
    if not issue_id:
        return {"message": "No Linear issue ID found in PR"}
    
    try:
        # Map PR states to Linear issue states
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
    # Extract Linear issue ID from branch name or commit messages
    issue_id = extract_linear_issue_id(event.workflow_run.head_branch)
    
    if not issue_id:
        return {"message": "No Linear issue ID found in workflow"}
    
    try:
        # Parse workflow status
        status, progress = parse_workflow_status(
            event.workflow_run.status,
            event.workflow_run.conclusion
        )
        
        # Update Linear issue
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