import re
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
    hunks: list[DiffHunk] = []
    
    # Split by files, keeping the delimiter
    file_diffs = re.split(r"^(?=diff --git )", raw_diff, flags=re.MULTILINE)
    
    for file_diff in file_diffs:
        if not file_diff.strip():
            continue
            
        file_path = ""
        # Extract filename from +++ b/... line
        filename_match = re.search(r"^\+\+\+ b/(.+)$", file_diff, flags=re.MULTILINE)
        if filename_match:
            file_path = filename_match.group(1).strip()
        else:
            # If it's a completely deleted file, +++ might be /dev/null
            filename_match = re.search(r"^--- a/(.+)$", file_diff, flags=re.MULTILINE)
            if filename_match:
                file_path = filename_match.group(1).strip()
            else:
                continue

        # Extract language from extension or filename
        if "." in file_path:
            language = file_path.split(".")[-1].lower()
        else:
            language = file_path.split("/")[-1].lower()
        
        # Split by hunks
        hunk_blocks = re.split(r"^(?=@@ )", file_diff, flags=re.MULTILINE)[1:]  # Skip the file header part
        
        for block in hunk_blocks:
            lines = block.splitlines()
            if not lines:
                continue
                
            header = lines[0]
            # Match @@ -old_start,old_length +new_start,new_length @@
            header_match = re.match(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", header)
            if not header_match:
                continue
                
            old_start = int(header_match.group(1))
            new_start = int(header_match.group(2))
            
            diff_lines = []
            curr_old = old_start
            curr_new = new_start
            
            for line_content in lines[1:]:
                if not line_content: continue
                
                prefix = line_content[0]
                content = line_content[1:]
                
                if prefix == " ":
                    diff_lines.append(DiffLine(line_number=curr_new, content=content, change_type="context"))
                    curr_old += 1
                    curr_new += 1
                elif prefix == "+":
                    diff_lines.append(DiffLine(line_number=curr_new, content=content, change_type="added"))
                    curr_new += 1
                elif prefix == "-":
                    diff_lines.append(DiffLine(line_number=curr_old, content=content, change_type="removed"))
                    curr_old += 1
                elif prefix == "\\":
                    # \ No newline at end of file
                    continue
            
            hunks.append(DiffHunk(
                file_path=file_path,
                language=language,
                lines=diff_lines,
                old_start=old_start,
                new_start=new_start
            ))
            
    return hunks
