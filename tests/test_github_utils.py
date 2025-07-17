import os
import pytest
from app.utils.github import verify_github_webhook, extract_linear_issue_id, parse_workflow_status

def test_extract_linear_issue_id():
    """Test Linear issue ID extraction from text"""
    # Test valid issue IDs
    assert extract_linear_issue_id("feat: implement feature ABC-123") == "ABC-123"
    assert extract_linear_issue_id("Fix bug [XYZ-789]") == "XYZ-789"
    assert extract_linear_issue_id("Multiple issues ABC-123 and XYZ-789") == "ABC-123"
    
    # Test invalid or missing issue IDs
    assert extract_linear_issue_id("No issue ID here") is None
    assert extract_linear_issue_id("Invalid ID: ABC123") is None
    assert extract_linear_issue_id("") is None

def test_parse_workflow_status():
    """Test workflow status parsing"""
    # Test completed workflows
    assert parse_workflow_status("completed", "success") == ("completed", 100.0)
    assert parse_workflow_status("completed", "failure") == ("blocked", None)
    assert parse_workflow_status("completed", "cancelled") == ("paused", None)
    assert parse_workflow_status("completed", "unknown") == ("in_progress", None)
    
    # Test in-progress workflows
    assert parse_workflow_status("in_progress", None) == ("in_progress", 50.0)
    
    # Test other states
    assert parse_workflow_status("queued", None) == ("backlog", None)
    assert parse_workflow_status("pending", None) == ("backlog", None)

def test_verify_github_webhook(monkeypatch):
    """Test GitHub webhook signature verification"""
    # Set up test environment
    test_secret = "test_secret"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", test_secret)
    
    # Test payload and signature
    payload = b'{"test": "data"}'
    import hmac
    import hashlib
    
    # Generate valid signature
    valid_signature = "sha256=" + hmac.new(
        test_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Test valid signature
    assert verify_github_webhook(valid_signature, payload) is True
    
    # Test invalid signatures
    assert verify_github_webhook("sha256=invalid", payload) is False
    assert verify_github_webhook("invalid_format", payload) is False
    assert verify_github_webhook("", payload) is False
    
    # Test missing secret
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET")
    with pytest.raises(ValueError):
        verify_github_webhook(valid_signature, payload) 