import re
from pathlib import Path


def preprocess_includes(filepath: Path):
    """
    Reads the file at 'filepath', processing any "include" directives,
    and returns a single string containing the preprocessed file content.

    This does not report circular includes, so that would become a infinite loop
    """
    INCLUDE_RE = re.compile(r"^\s*include\s+([^\n]+)\s*$", re.IGNORECASE)

    def read_file(file_path):
        with open(file_path, "r") as file:
            return file.readlines()

    lines = read_file(filepath)
    i = 0
    while i < len(lines):
        match = INCLUDE_RE.match(lines[i])
        if match:
            included_file_path = match.group(1)
            included_lines = read_file(included_file_path)
            lines[i : i + 1] = included_lines
        else:
            i += 1

    return "".join(lines)
