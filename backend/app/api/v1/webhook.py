import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.core.security import verify_github_webhook
from app.services.github_auth import get_installation_access_token
from app.services.github_client import get_pr_diff
from app.services.diff_parser import parse_diff, DiffHunk

router = APIRouter()
logger = get_logger(__name__)


def _hunk_to_dict(hunk: DiffHunk) -> dict:
    return {
        "file_path": hunk.file_path,
        "language": hunk.language,
        "old_start": hunk.old_start,
        "new_start": hunk.new_start,
        "lines": [
            {"line_number": l.line_number, "content": l.content, "change_type": l.change_type}
            for l in hunk.lines
        ],
    }


@router.post("/webhook/github", summary="GitHub Webhook Receiver", tags=["webhook"])
async def github_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    body: bytes = Depends(verify_github_webhook),
) -> JSONResponse:
    """Receive GitHub webhook events, fetch the PR diff, and return parsed hunks."""
    payload = json.loads(body)
    action = payload.get("action", "")

    logger.info(
        "github_webhook_received",
        github_event=x_github_event,
        action=action,
        repo=payload.get("repository", {}).get("full_name", "unknown"),
    )

    if x_github_event == "pull_request" and action in ("opened", "synchronize", "reopened"):
        pr_number = payload.get("pull_request", {}).get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")
        installation_id = str(payload.get("installation", {}).get("id", ""))

        logger.info("pr_review_started", pr_number=pr_number, repo=repo_full_name)

        try:
            token = await get_installation_access_token(installation_id)
            raw_diff = await get_pr_diff(repo_full_name, pr_number, token)
            hunks = parse_diff(raw_diff)

            unique_files = len(set(h.file_path for h in hunks))
            logger.info(
                "pr_diff_parsed",
                pr_number=pr_number,
                repo=repo_full_name,
                files=unique_files,
                hunks=len(hunks),
            )

            # TODO: enqueue Celery task (Day 5)
            return JSONResponse(
                content={
                    "status": "accepted",
                    "repo": repo_full_name,
                    "pr_number": pr_number,
                    "files_changed": unique_files,
                    "total_hunks": len(hunks),
                    "hunks": [_hunk_to_dict(h) for h in hunks],
                },
                status_code=202,
            )
        except Exception as exc:
            logger.error("pr_review_failed", pr_number=pr_number, repo=repo_full_name, error=str(exc))
            raise HTTPException(status_code=500, detail=f"Failed to process PR diff: {exc}")

    return JSONResponse(content={"status": "ignored", "github_event": x_github_event})
