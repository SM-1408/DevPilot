import re
from pathlib import Path


# ============================================================
# JAVASCRIPT ANALYZER
# ============================================================

def analyze_javascript_file(file_path: str):
    """
    Analyze a JavaScript source file.

    Provides:
    - lines
    - classes
    - functions
    - imports
    - TODO/FIXME
    - basic complexity
    - code smells
    - security issues
    """

    path = Path(file_path)

    source_code = path.read_text(
        encoding="utf-8"
    )

    lines = source_code.splitlines()

    classes = find_classes(source_code)
    functions = find_functions(source_code)
    imports = find_imports(source_code)
    todos = find_todos(source_code)

    security_issues = find_security_issues(
        source_code
    )

    analyzed_functions = []

    for function in functions:

        complexity = calculate_function_complexity(
            function["body"]
        )

        analyzed_functions.append({
            "name": function["name"],
            "line": function["line"],
            "complexity": complexity,
            "level": complexity_level(complexity),
            "smells": find_function_smells(function),
        })

    return {
        "file": str(path),
        "language": "JavaScript",
        "lines": len(lines),
        "functions": analyzed_functions,
        "classes": classes,
        "imports": imports,
        "todos": todos,
        "security_smells": security_issues,
        "duplicates": [],
        "unused_imports": [],
        "security_issues": security_issues,
    }


# ============================================================
# CLASS DETECTION
# ============================================================

def find_classes(source_code: str):

    pattern = re.compile(
        r"\bclass\s+([A-Za-z_$][\w$]*)"
    )

    return [
        match.group(1)
        for match in pattern.finditer(source_code)
    ]


# ============================================================
# FUNCTION DETECTION
# ============================================================

def find_functions(source_code: str):

    lines = source_code.splitlines()

    functions = []

    patterns = [
        re.compile(
            r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\("
        ),
        re.compile(
            r"\b(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)\s*="
            r"\s*(?:async\s*)?\([^)]*\)\s*=>"
        ),
        re.compile(
            r"\b(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)\s*="
            r"\s*(?:async\s*)?"
            r"[A-Za-z_$][\w$]*\s*=>"
        ),
    ]

    for index, line in enumerate(lines):

        for pattern in patterns:

            match = pattern.search(line)

            if not match:
                continue

            name = match.group(1)

            body = collect_function_body(
                lines,
                index
            )

            functions.append({
                "name": name,
                "line": index + 1,
                "body": body,
            })

            break

    return functions


# ============================================================
# COLLECT FUNCTION BODY
# ============================================================

def collect_function_body(
    lines,
    start_index
):

    body = []

    brace_count = 0
    started = False

    for line in lines[start_index:]:

        body.append(line)

        opening = line.count("{")
        closing = line.count("}")

        if opening > 0:
            started = True

        if started:

            brace_count += opening
            brace_count -= closing

        if started and brace_count <= 0:
            break

    return "\n".join(body)


# ============================================================
# IMPORT DETECTION
# ============================================================

def find_imports(source_code: str):

    imports = []

    patterns = [
        r"^\s*import\s+.+",
        r"^\s*const\s+.+\s*=\s*require\s*\(.+\)",
    ]

    for line in source_code.splitlines():

        stripped = line.strip()

        for pattern in patterns:

            if re.match(pattern, stripped):
                imports.append(stripped)
                break

    return imports


# ============================================================
# TODO / FIXME
# ============================================================

def find_todos(source_code: str):

    todos = []

    pattern = re.compile(
        r"//\s*(TODO|FIXME)\b[:\s]*(.*)",
        re.IGNORECASE
    )

    for line_number, line in enumerate(
        source_code.splitlines(),
        start=1
    ):

        match = pattern.search(line)

        if not match:
            continue

        issue_type = match.group(1).upper()
        message = match.group(2).strip()

        todos.append({
            "line": line_number,
            "type": issue_type,
            "message": (
                message
                or f"{issue_type} found"
            ),
        })

    return todos


# ============================================================
# COMPLEXITY
# ============================================================

def calculate_function_complexity(
    function_body: str
):

    complexity = 1

    complexity += len(
        re.findall(
            r"\bif\s*\(",
            function_body
        )
    )

    complexity += len(
        re.findall(
            r"\b(for|while)\s*\(",
            function_body
        )
    )

    complexity += len(
        re.findall(
            r"\bcase\b",
            function_body
        )
    )

    complexity += len(
        re.findall(
            r"\bcatch\s*\(",
            function_body
        )
    )

    complexity += function_body.count("?")

    complexity += len(
        re.findall(
            r"&&|\|\|",
            function_body
        )
    )

    return complexity


def complexity_level(complexity):

    if complexity <= 5:
        return "LOW"

    if complexity <= 10:
        return "MEDIUM"

    if complexity <= 20:
        return "HIGH"

    return "VERY HIGH"


# ============================================================
# FUNCTION CODE SMELLS
# ============================================================

def find_function_smells(function):

    smells = []

    body = function["body"]
    line = function["line"]
    name = function["name"]

    function_lines = len(
        body.splitlines()
    )

    # --------------------------------------------------------
    # Long function
    # --------------------------------------------------------

    if function_lines > 50:

        smells.append({
            "line": line,
            "type": "LONG_FUNCTION",
            "severity": "MEDIUM",
            "message": (
                f"Function '{name}' contains "
                f"{function_lines} lines."
            ),
        })

    # --------------------------------------------------------
    # Deep nesting
    # --------------------------------------------------------

    max_depth = 0
    current_depth = 0

    for character in body:

        if character == "{":

            current_depth += 1

            max_depth = max(
                max_depth,
                current_depth
            )

        elif character == "}":

            current_depth -= 1

    if max_depth > 4:

        smells.append({
            "line": line,
            "type": "DEEP_NESTING",
            "severity": "MEDIUM",
            "message": (
                f"Function '{name}' has "
                "deep nesting."
            ),
        })

    # --------------------------------------------------------
    # console.log
    # --------------------------------------------------------

    if "console.log(" in body:

        smells.append({
            "line": line,
            "type": "CONSOLE_LOG",
            "severity": "LOW",
            "message": (
                "console.log() should generally "
                "be replaced by proper logging."
            ),
        })

    return smells


# ============================================================
# SECURITY DETECTION
# ============================================================

def find_security_issues(
    source_code: str
):

    issues = []

    # --------------------------------------------------------
    # eval()
    # --------------------------------------------------------

    eval_pattern = re.compile(
        r"\beval\s*\("
    )

    for match in eval_pattern.finditer(
        source_code
    ):

        line = (
            source_code[:match.start()]
            .count("\n")
            + 1
        )

        issues.append({
            "line": line,
            "type": "DANGEROUS_EVAL",
            "severity": "HIGH",
            "message": (
                "eval() can execute arbitrary "
                "JavaScript code."
            ),
        })

    # --------------------------------------------------------
    # Function constructor
    # --------------------------------------------------------

    function_pattern = re.compile(
        r"\bnew\s+Function\s*\("
    )

    for match in function_pattern.finditer(
        source_code
    ):

        line = (
            source_code[:match.start()]
            .count("\n")
            + 1
        )

        issues.append({
            "line": line,
            "type": "DANGEROUS_FUNCTION",
            "severity": "HIGH",
            "message": (
                "new Function() can execute "
                "dynamically generated code."
            ),
        })

    # --------------------------------------------------------
    # Hardcoded secrets
    # --------------------------------------------------------

    secret_pattern = re.compile(
        r"""
        (?i)
        (password|passwd|secret|api[_-]?key|token)
        \s*=\s*
        ["'][^"']+["']
        """,
        re.VERBOSE,
    )

    for match in secret_pattern.finditer(
        source_code
    ):

        line = (
            source_code[:match.start()]
            .count("\n")
            + 1
        )

        issues.append({
            "line": line,
            "type": "HARDCODED_SECRET",
            "severity": "HIGH",
            "message": (
                "Possible hardcoded secret detected."
            ),
        })

    return issues