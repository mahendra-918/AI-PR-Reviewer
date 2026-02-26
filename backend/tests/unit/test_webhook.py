import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.config import settings
from tests.unit.test_security import generate_signature


SAMPLE_DIFF = """diff --git a/main.py b/main.py
index e69de29..d95f3ad 100644
--- a/main.py
+++ b/main.py
@@ -1,2 +1,3 @@
 def hello():
-    return False
+    return True
"""


@pytest.mark.asyncio
async def test_webhook_ignores_non_pr_events(async_client: AsyncClient):
    body = b'{"action": "created"}'
    signature = generate_signature(settings.github_webhook_secret, body)
    headers = {
        "X-GitHub-Event": "issue_comment",
        "X-Hub-Signature-256": signature
    }

    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "github_event": "issue_comment"}


@pytest.mark.asyncio
async def test_webhook_ignores_unsupported_pr_actions(async_client: AsyncClient):
    body = b'{"action": "closed", "pull_request": {"number": 1}}'
    signature = generate_signature(settings.github_webhook_secret, body)
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature
    }

    response = await async_client.post("/api/v1/webhook/github", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "github_event": "pull_request"}


@pytest.mark.asyncio
async def test_webhook_accepts_pr_opened(async_client: AsyncClient):
    import json as _json
    pr_payload = _json.dumps({
        "action": "opened",
        "pull_request": {"number": 42},
        "repository": {"full_name": "test/repo"},
        "installation": {"id": 99},
    }).encode()
    signature = generate_signature(settings.github_webhook_secret, pr_payload)
    headers = {"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": signature}

    with patch("app.api.v1.webhook.get_installation_access_token", new_callable=AsyncMock, return_value="mock-token"), \
         patch("app.api.v1.webhook.get_pr_diff", new_callable=AsyncMock, return_value=SAMPLE_DIFF):
        response = await async_client.post("/api/v1/webhook/github", content=pr_payload, headers=headers)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["pr_number"] == 42
    assert data["repo"] == "test/repo"
    assert data["files_changed"] == 1
    assert data["total_hunks"] == 1
    assert data["hunks"][0]["file_path"] == "main.py"
    assert data["hunks"][0]["language"] == "py"


@pytest.mark.asyncio
async def test_webhook_accepts_pr_synchronize(async_client: AsyncClient):
    import json as _json
    pr_payload = _json.dumps({
        "action": "synchronize",
        "pull_request": {"number": 42},
        "repository": {"full_name": "test/repo"},
        "installation": {"id": 99},
    }).encode()
    signature = generate_signature(settings.github_webhook_secret, pr_payload)
    headers = {"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": signature}

    with patch("app.api.v1.webhook.get_installation_access_token", new_callable=AsyncMock, return_value="mock-token"), \
         patch("app.api.v1.webhook.get_pr_diff", new_callable=AsyncMock, return_value=SAMPLE_DIFF):
        response = await async_client.post("/api/v1/webhook/github", content=pr_payload, headers=headers)

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
