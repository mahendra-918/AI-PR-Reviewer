import hashlib
import hmac
import json
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import verify_github_webhook

client = TestClient(app)


def generate_signature(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def test_verify_github_webhook_missing_header():
    response = client.post("/api/v1/webhook/github", json={"zen": "test"}, headers={"X-GitHub-Event": "ping"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-Hub-Signature-256 header"


def test_verify_github_webhook_invalid_signature():
    
    body = json.dumps({"zen": "test"}).encode("utf-8")
    headers = {
        "X-GitHub-Event": "ping",
        "X-Hub-Signature-256": "sha256=invalid_hash_value"
    }
    
    response = client.post(
        "/api/v1/webhook/github", 
        content=body, 
        headers=headers
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid webhook signature"


def test_verify_github_webhook_valid_signature():
    
    body = b'{"zen": "test"}'
    secret = settings.github_webhook_secret
    signature = generate_signature(secret, body)
    
    headers = {
        "X-GitHub-Event": "ping",
        "X-Hub-Signature-256": signature
    }
    
    response = client.post(
        "/api/v1/webhook/github", 
        content=body, 
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
