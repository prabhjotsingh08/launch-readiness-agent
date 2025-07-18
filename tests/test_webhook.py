import os
from app.utils.webhook_test import (
    generate_github_signature,
    SAMPLE_PUSH_EVENT,
    SAMPLE_PR_EVENT,
    SAMPLE_WORKFLOW_EVENT
)

def main():
    # Get webhook secret from environment
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "your_webhook_secret_here")
    
    # Generate signatures for each event type
    push_signature = generate_github_signature(SAMPLE_PUSH_EVENT, webhook_secret)
    pr_signature = generate_github_signature(SAMPLE_PR_EVENT, webhook_secret)
    workflow_signature = generate_github_signature(SAMPLE_WORKFLOW_EVENT, webhook_secret)
    
    print("\nTo test GitHub webhooks in Swagger UI (http://127.0.0.1:8000/docs):")
    
    print("\n1. Testing Push Event:")
    print("Headers required:")
    print('X-Hub-Signature-256:', push_signature)
    print('X-GitHub-Event: push')
    print("\nRequest Body:")
    print(SAMPLE_PUSH_EVENT)
    
    print("\n2. Testing Pull Request Event:")
    print("Headers required:")
    print('X-Hub-Signature-256:', pr_signature)
    print('X-GitHub-Event: pull_request')
    print("\nRequest Body:")
    print(SAMPLE_PR_EVENT)
    
    print("\n3. Testing Workflow Run Event:")
    print("Headers required:")
    print('X-Hub-Signature-256:', workflow_signature)
    print('X-GitHub-Event: workflow_run')
    print("\nRequest Body:")
    print(SAMPLE_WORKFLOW_EVENT)

if __name__ == "__main__":
    main() 