from pathlib import Path


def get_source_context(
    file_path: str,
    line: int,
    context: int = 5
):
    """
    Return source code around a specific line.

    Args:
        file_path: Path to the source file.
        line: Target line number.
        context: Number of lines before and after target line.

    Returns:
        Dictionary containing source lines and metadata.
    """

    path = Path(file_path)

    # ---------------------------------------------------------
    # Validate file
    # ---------------------------------------------------------

    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    # ---------------------------------------------------------
    # Validate line number
    # ---------------------------------------------------------

    if line < 1:
        raise ValueError(
            "Line number must be greater than 0"
        )

    if context < 0:
        raise ValueError(
            "Context cannot be negative"
        )

    # ---------------------------------------------------------
    # Read source
    # ---------------------------------------------------------

    try:
        source_lines = path.read_text(
            encoding="utf-8"
        ).splitlines()

    except UnicodeDecodeError as error:
        raise ValueError(
            f"Unable to decode source file: {error}"
        )

    # ---------------------------------------------------------
    # Check requested line
    # ---------------------------------------------------------

    total_lines = len(source_lines)

    if line > total_lines:
        raise ValueError(
            f"Line {line} does not exist. "
            f"File contains {total_lines} lines."
        )

    # ---------------------------------------------------------
    # Calculate context range
    # ---------------------------------------------------------

    start_line = max(
        1,
        line - context
    )

    end_line = min(
        total_lines,
        line + context
    )

    # ---------------------------------------------------------
    # Build source result
    # ---------------------------------------------------------

    source = []

    for line_number in range(
        start_line,
        end_line + 1
    ):
        source.append({
            "line": line_number,
            "code": source_lines[line_number - 1],
            "is_target": line_number == line
        })

    return {
        "file": str(path),
        "target_line": line,
        "start_line": start_line,
        "end_line": end_line,
        "total_lines": total_lines,
        "source": source
    }