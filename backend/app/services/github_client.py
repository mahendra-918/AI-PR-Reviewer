import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_pr_diff(repo_full_name: str, pr_number: int, installation_token: str) -> str:
    """Fetch the raw unified diff for a pull request from GitHub's API."""
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        logger.info("pr_diff_fetched", repo=repo_full_name, pr_number=pr_number, size=len(response.text))
        return response.text
