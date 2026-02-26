import time
import jwt
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _load_private_key() -> str:
    with open(settings.github_private_key_path, "r") as f:
        return f.read()


def _generate_jwt() -> str:
    """Generate a signed JWT for authenticating as the GitHub App."""
    private_key = _load_private_key()
    now = int(time.time())
    payload = {
        "iat": now - 60,        # issued 60s ago to allow clock drift
        "exp": now + (10 * 60), # expires in 10 minutes (max allowed)
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


async def get_installation_access_token(installation_id: str) -> str:
    """Exchange the GitHub App JWT for a short-lived installation access token."""
    app_jwt = _generate_jwt()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        token = response.json()["token"]
        logger.info("installation_token_fetched", installation_id=installation_id)
        return token
