import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.unit.test_security import generate_signature


@pytest.mark.asyncio
async def test_webhook_ignores_non_pr_events(async_client: AsyncClient):
    """Ensure non-PR events like 'issue_comment' are ignored."""
    body = b'{"action": "created"}'
    signature = generate_signature(settings.github_webhook_secret, body)
    
    headers = {
        "X-GitHub-Event": "issue_comment",
        "X-Hub-Signature-256": signature
    }
    
    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "event": "issue_comment"}


@pytest.mark.asyncio
async def test_webhook_ignores_unsupported_pr_actions(async_client: AsyncClient):
    """Ensure PR actions like 'closed' or 'labeled' are ignored."""
    body = b'{"action": "closed", "pull_request": {"number": 1}}'
    signature = generate_signature(settings.github_webhook_secret, body)
    
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature
    }
    
    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "event": "pull_request"}


@pytest.mark.asyncio
async def test_webhook_accepts_pr_opened(async_client: AsyncClient):
    """Ensure 'opened' PR events are accepted for review."""
    body = b'{"action": "opened", "pull_request": {"number": 42}, "repository": {"full_name": "test/repo"}}'
    signature = generate_signature(settings.github_webhook_secret, body)
    
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature
    }
    
    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted", 
        "pr_number": 42, 
        "repo": "test/repo"
    }


@pytest.mark.asyncio
async def test_webhook_accepts_pr_synchronize(async_client: AsyncClient):
    """Ensure 'synchronize' (new commits) PR events are accepted for review."""
    body = b'{"action": "synchronize", "pull_request": {"number": 42}, "repository": {"full_name": "test/repo"}}'
    signature = generate_signature(settings.github_webhook_secret, body)
    
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature
    }
    
    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted", 
        "pr_number": 42, 
        "repo": "test/repo"
    }
