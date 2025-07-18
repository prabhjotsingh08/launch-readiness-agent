import hmac
import hashlib
import json

# Your webhook secret from .env
WEBHOOK_SECRET = "launchreadinessagentactivated"

# Complete GitHub push event payload with all required fields
payload = {
    "ref": "refs/heads/main",
    "before": "0000000000000000000000000000000000000000",
    "after": "abc123def456789012345678901234567890abcd",
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

# Generate signatures for both compact and pretty formatting
secret_bytes = WEBHOOK_SECRET.encode('utf-8')

# Compact signature (what the endpoint will try first)
compact_payload = json.dumps(payload, separators=(',', ':'))
compact_signature = hmac.new(secret_bytes, compact_payload.encode('utf-8'), hashlib.sha256).hexdigest()

# Pretty signature (fallback)
pretty_payload = json.dumps(payload, indent=2)
pretty_signature = hmac.new(secret_bytes, pretty_payload.encode('utf-8'), hashlib.sha256).hexdigest()

print("\nSwagger UI Testing Instructions:")
print("--------------------------------")
print("\n1. Go to http://127.0.0.1:8000/docs")
print("2. Find and expand 'POST /api/github/webhook'")
print("3. Click 'Try it out'")

print("\n4. Enter these headers:")
print("-" * 30)
print("X-Hub-Signature-256:", f"sha256={compact_signature}")
print("X-GitHub-Event: push")

print("\n5. In the Request body field, paste this JSON:")
print("-" * 30)
print(json.dumps(payload, indent=2))

print("\nAlternative signatures (if the first doesn't work):")
print(f"Compact format signature: sha256={compact_signature}")
print(f"Pretty format signature:  sha256={pretty_signature}")

print("\nNow the endpoint will try both signature formats automatically!")
print("Just use the compact signature above and paste the JSON as shown.") 