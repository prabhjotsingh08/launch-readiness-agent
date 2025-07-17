import os
import hmac
import hashlib
import re
from typing import Optional, Tuple

def verify_github_webhook(signature: str, payload: bytes) -> bool:
    """
    Verify GitHub webhook signature
    
    Args:
        signature: The signature from X-Hub-Signature-256 header
        payload: Raw request body bytes
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature or not signature.startswith("sha256="):
        return False

    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
    if not secret:
        raise ValueError("GITHUB_WEBHOOK_SECRET environment variable is not set")

    expected_signature = "sha256=" + hmac.new(
        secret,
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

def extract_linear_issue_id(text: str) -> Optional[str]:
    """
    Extract Linear issue ID from text (commit message or PR title/description)
    
    Args:
        text: Text to search for Linear issue ID
    
    Returns:
        Optional[str]: Linear issue ID if found, None otherwise
    """
    # Linear issue format: ABC-123
    pattern = r'([A-Z]{2,}-\d+)'
    match = re.search(pattern, text)
    return match.group(1) if match else None

def parse_workflow_status(status: str, conclusion: Optional[str]) -> Tuple[str, Optional[float]]:
    """
    Parse GitHub workflow status and conclusion into Linear project status and progress
    
    Args:
        status: GitHub workflow status
        conclusion: GitHub workflow conclusion
    
    Returns:
        Tuple[str, Optional[float]]: Linear project status and progress percentage
    """
    if status == "completed":
        if conclusion == "success":
            return "completed", 100.0
        elif conclusion == "failure":
            return "blocked", None
        elif conclusion == "cancelled":
            return "paused", None
        else:
            return "in_progress", None
    elif status == "in_progress":
        return "in_progress", 50.0
    else:
        return "backlog", None 