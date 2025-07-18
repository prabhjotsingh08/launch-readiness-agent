import hmac
import hashlib
import json

def generate_github_signature(payload: dict, secret: str) -> str:
    """
    Generate GitHub webhook signature for testing
    
    Args:
        payload: The webhook payload as a dictionary
        secret: The webhook secret
    
    Returns:
        str: The signature in sha256=... format
    """
    payload_bytes = json.dumps(payload).encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    signature = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

# Example payloads for testing
SAMPLE_PUSH_EVENT = {
    "ref": "refs/heads/main",
    "repository": {
        "id": 123,
        "name": "test-repo",
        "full_name": "org/test-repo",
        "private": False,
        "owner": {
            "login": "testuser",
            "id": 456,
            "type": "User"
        }
    },
    "commits": [
        {
            "id": "abc123",
            "message": "feat: implement new feature ABC-123",
            "timestamp": "2024-02-20T12:00:00Z",
            "url": "https://github.com/org/repo/commit/abc123",
            "author": {
                "login": "testuser",
                "id": 456,
                "type": "User"
            }
        }
    ],
    "sender": {
        "login": "testuser",
        "id": 456,
        "type": "User"
    }
}

SAMPLE_PR_EVENT = {
    "action": "opened",
    "pull_request": {
        "id": 789,
        "number": 42,
        "state": "open",
        "title": "Feature: Implement XYZ-789",
        "body": "Implements the new feature described in XYZ-789",
        "user": {
            "login": "testuser",
            "id": 456,
            "type": "User"
        },
        "created_at": "2024-02-20T12:00:00Z",
        "updated_at": "2024-02-20T12:00:00Z",
        "merged_at": None,
        "head": {
            "ref": "feature/xyz-789",
            "sha": "def456"
        },
        "base": {
            "ref": "main",
            "sha": "abc123"
        }
    },
    "repository": {
        "id": 123,
        "name": "test-repo",
        "full_name": "org/test-repo",
        "private": False,
        "owner": {
            "login": "testuser",
            "id": 456,
            "type": "User"
        }
    },
    "sender": {
        "login": "testuser",
        "id": 456,
        "type": "User"
    }
}

SAMPLE_WORKFLOW_EVENT = {
    "action": "completed",
    "workflow_run": {
        "id": 123456,
        "name": "CI/CD Pipeline",
        "status": "completed",
        "conclusion": "success",
        "workflow_id": 789,
        "head_branch": "feature/abc-123",
        "head_sha": "def456",
        "run_number": 42,
        "event": "push",
        "url": "https://github.com/org/repo/actions/runs/123456",
        "created_at": "2024-02-20T12:00:00Z",
        "updated_at": "2024-02-20T12:10:00Z"
    },
    "repository": {
        "id": 123,
        "name": "test-repo",
        "full_name": "org/test-repo",
        "private": False,
        "owner": {
            "login": "testuser",
            "id": 456,
            "type": "User"
        }
    },
    "sender": {
        "login": "testuser",
        "id": 456,
        "type": "User"
    }
} 