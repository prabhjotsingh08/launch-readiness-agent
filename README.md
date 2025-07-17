# Launch Readiness Agent

A FastAPI-based service that integrates GitHub webhooks with Linear project management, automatically syncing project status, issues, and CI/CD events.

## Features

- Pull and manage Linear projects
- Automatic synchronization of GitHub events with Linear issues
- Support for:
  - Push events
  - Pull request events
  - Workflow run events
- Automatic issue updates based on commit messages and PR titles
- Secure webhook handling with signature verification

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd launch-readiness-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:
- `LINEAR_API_KEY`: Your Linear API key
- `GITHUB_WEBHOOK_SECRET`: Secret for GitHub webhook verification
- `GITHUB_API_TOKEN`: GitHub personal access token (if needed)

## Running the Service

Start the service:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Linear Project Endpoints

#### GET /api/linear/projects
List all projects from Linear.

Response:
```json
{
  "success": true,
  "message": "Projects retrieved successfully",
  "data": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "state": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "target_date": "datetime",
      "progress": 0
    }
  ]
}
```

#### GET /api/linear/projects/{project_id}
Get details of a specific project.

Response:
```json
{
  "success": true,
  "message": "Project retrieved successfully",
  "data": {
    "id": "string",
    "name": "string",
    "description": "string",
    "state": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "target_date": "datetime",
    "progress": 0
  }
}
```

#### PATCH /api/linear/projects/{project_id}
Update a project's status.

Request:
```json
{
  "state": "string",
  "progress": 0,
  "description": "string"
}
```

### GitHub Webhook Endpoint

#### POST /api/github/webhook
Handles GitHub webhook events. Requires the following headers:
- `X-Hub-Signature-256`: GitHub webhook signature
- `X-GitHub-Event`: Event type (push, pull_request, workflow_run)

## Testing

### Unit Tests
Run the test suite:
```bash
pytest
```

### Postman Collection

Import the provided Postman collection for testing the API endpoints:

1. Set up environment variables in Postman:
   - `BASE_URL`: Your API base URL (e.g., `http://localhost:8000`)
   - `GITHUB_WEBHOOK_SECRET`: Your GitHub webhook secret

2. Use the following test examples:

#### Linear Project Update
```json
{
  "state": "in_progress",
  "progress": 50,
  "description": "Project is halfway complete"
}
```

#### GitHub Webhook - Push Event
```json
{
  "ref": "refs/heads/main",
  "commits": [
    {
      "id": "abc123",
      "message": "feat: implement new feature ABC-123",
      "timestamp": "2024-02-20T12:00:00Z",
      "url": "https://github.com/org/repo/commit/abc123"
    }
  ]
}
```

## GitHub Webhook Setup

1. Go to your repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - Payload URL: `your-domain/api/github/webhook`
   - Content type: `application/json`
   - Secret: Your `GITHUB_WEBHOOK_SECRET`
   - Events: Select push, pull requests, and workflow runs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT 