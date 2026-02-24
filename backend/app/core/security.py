import hashlib
import hmac

from fastapi import HTTPException, Request, status

from app.core.config import settings


async def verify_github_webhook(request: Request) -> bytes:
    """Verify GitHub webhook HMAC-SHA256 signature. Raises 401 if invalid."""
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header",
        )

    body = await request.body()
    secret = settings.github_webhook_secret.encode("utf-8")
    expected_sig = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_sig, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    return body
