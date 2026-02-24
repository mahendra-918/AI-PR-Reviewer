from dataclasses import dataclass, field


@dataclass
class DiffLine:
    line_number: int
    content: str
    change_type: str  # "added" | "removed" | "context"


@dataclass
class DiffHunk:
    file_path: str
    language: str
    lines: list[DiffLine] = field(default_factory=list)
    old_start: int = 0
    new_start: int = 0


def parse_diff(raw_diff: str) -> list[DiffHunk]:
    """Parse a raw git diff string into a list of DiffHunk objects."""
    raise NotImplementedError("Diff parser will be implemented on Day 4")
