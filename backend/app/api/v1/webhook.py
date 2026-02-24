import json

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.core.security import verify_github_webhook

router = APIRouter()
logger = get_logger(__name__)


@router.post("/webhook/github", summary="GitHub Webhook Receiver", tags=["webhook"])
async def github_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    body: bytes = Depends(verify_github_webhook),
) -> JSONResponse:
    """Receive GitHub webhook events and enqueue a review task for PR events."""
    payload = json.loads(body)
    action = payload.get("action", "")

    logger.info(
        "github_webhook_received",
        event=x_github_event,
        action=action,
        repo=payload.get("repository", {}).get("full_name", "unknown"),
    )

    if x_github_event == "pull_request" and action in ("opened", "synchronize", "reopened"):
        pr_number = payload.get("pull_request", {}).get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")

        logger.info("review_task_enqueued", pr_number=pr_number, repo=repo_full_name)

        # TODO: enqueue Celery task (Day 5)

        return JSONResponse(
            content={
                "status": "accepted",
                "pr_number": pr_number,
                "repo": repo_full_name,
            },
            status_code=202,
        )

    return JSONResponse(content={"status": "ignored", "event": x_github_event})
