from pydantic import BaseModel
from typing import Literal


class ParsedLineSchema(BaseModel):
    line_number: int
    content: str
    change_type: Literal["added", "removed", "context"]


class ParsedHunkSchema(BaseModel):
    file_path: str
    language: str
    old_start: int
    new_start: int
    lines: list[ParsedLineSchema]


class PRReviewParseResponse(BaseModel):
    status: str
    repo: str
    pr_number: int
    files_changed: int
    total_hunks: int
    hunks: list[ParsedHunkSchema]
