import re
from pathlib import Path


# ============================================================
# JAVA ANALYZER
# ============================================================

def analyze_java_file(file_path: str):
    """
    Analyze a Java source file.

    This analyzer focuses on structural information first:
    - lines
    - classes
    - methods
    - imports
    - TODO/FIXME
    - basic complexity
    - basic code smells
    - basic security issues
    """

    path = Path(file_path)

    source_code = path.read_text(
        encoding="utf-8"
    )

    lines = source_code.splitlines()

    classes = find_classes(source_code)

    methods = find_methods(source_code)

    imports = find_imports(source_code)

    todos = find_todos(source_code)

    security_issues = find_security_issues(
        source_code,
        lines
    )

    functions = []

    for method in methods:

        complexity = calculate_method_complexity(
            method["body"]
        )

        functions.append({
            "name": method["name"],
            "line": method["line"],
            "complexity": complexity,
            "level": complexity_level(
                complexity
            ),
            "smells": find_method_smells(
                method
            ),
        })

    return {
        "file": str(path),

        "language": "Java",

        "lines": len(lines),

        "functions": functions,

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
        for match in pattern.finditer(
            source_code
        )
    ]


# ============================================================
# METHOD DETECTION
# ============================================================

def find_methods(source_code: str):

    lines = source_code.splitlines()

    methods = []

    method_pattern = re.compile(
        r"""
        (?:
            public\s+|
            private\s+|
            protected\s+|
            static\s+|
            final\s+|
            synchronized\s+|
            abstract\s+|
            native\s+|
            strictfp\s+
        )*
        (?:
            <[^>]+>\s*
        )?
        [\w<>\[\], ?]+\s+
        ([A-Za-z_$][\w$]*)\s*
        \([^;{}]*\)\s*
        (?:throws\s+[^{]+)?
        \{
        """,
        re.VERBOSE,
    )

    for index, line in enumerate(lines):

        match = method_pattern.search(line)

        if not match:
            continue

        name = match.group(1)

        body = collect_method_body(
            lines,
            index
        )

        methods.append({
            "name": name,
            "line": index + 1,
            "body": body,
        })

    return methods


# ============================================================
# COLLECT METHOD BODY
# ============================================================

def collect_method_body(
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

    pattern = re.compile(
        r"^\s*import\s+(?:static\s+)?([^;]+);",
        re.MULTILINE,
    )

    return [
        f"import {match.group(1)};"
        for match in pattern.finditer(
            source_code
        )
    ]


# ============================================================
# TODO / FIXME
# ============================================================

def find_todos(source_code: str):

    todos = []

    pattern = re.compile(
        r"//\s*(TODO|FIXME)\b[:\s]*(.*)",
        re.IGNORECASE,
    )

    for line_number, line in enumerate(
        source_code.splitlines(),
        start=1,
    ):

        match = pattern.search(line)

        if not match:
            continue

        issue_type = match.group(1).upper()

        message = match.group(2).strip()

        todos.append({
            "line": line_number,
            "type": issue_type,
            "message": message
            or f"{issue_type} found",
        })

    return todos


# ============================================================
# COMPLEXITY
# ============================================================

def calculate_method_complexity(
    method_body: str
):

    complexity = 1

    # Branches
    complexity += len(
        re.findall(
            r"\bif\s*\(",
            method_body
        )
    )

    # Loops
    complexity += len(
        re.findall(
            r"\b(for|while)\s*\(",
            method_body
        )
    )

    # Switch cases
    complexity += len(
        re.findall(
            r"\bcase\b",
            method_body
        )
    )

    # Catch blocks
    complexity += len(
        re.findall(
            r"\bcatch\s*\(",
            method_body
        )
    )

    # Ternary operators
    complexity += method_body.count("?")

    # Boolean conditions
    complexity += len(
        re.findall(
            r"&&|\|\|",
            method_body
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
# METHOD CODE SMELLS
# ============================================================

def find_method_smells(method):

    smells = []

    body = method["body"]

    line = method["line"]

    # --------------------------------------------------------
    # Long method
    # --------------------------------------------------------

    method_lines = len(
        body.splitlines()
    )

    if method_lines > 50:

        smells.append({
            "line": line,
            "type": "LONG_METHOD",
            "severity": "MEDIUM",
            "message": (
                f"Method '{method['name']}' "
                f"contains {method_lines} lines."
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
                f"Method '{method['name']}' "
                "has deep nesting."
            ),
        })

    # --------------------------------------------------------
    # System.out
    # --------------------------------------------------------

    if "System.out.println" in body:

        smells.append({
            "line": line,
            "type": "SYSTEM_OUT",
            "severity": "LOW",
            "message": (
                "System.out.println() should "
                "generally be replaced by proper logging."
            ),
        })

    return smells


# ============================================================
# SECURITY DETECTION
# ============================================================

def find_security_issues(
    source_code,
    lines
):

    issues = []

    # --------------------------------------------------------
    # Runtime execution
    # --------------------------------------------------------

    dangerous_patterns = [
        (
            r"Runtime\.getRuntime\(\)\.exec",
            "DANGEROUS_EXEC",
            "HIGH",
            "Runtime.exec() can execute operating-system commands."
        ),
        (
            r"ProcessBuilder\s*\(",
            "PROCESS_EXECUTION",
            "HIGH",
            "ProcessBuilder can execute operating-system commands."
        ),
    ]

    for pattern, issue_type, severity, message in dangerous_patterns:

        for match in re.finditer(
            pattern,
            source_code
        ):

            line = (
                source_code[:match.start()]
                .count("\n")
                + 1
            )

            issues.append({
                "line": line,
                "type": issue_type,
                "severity": severity,
                "message": message,
            })

    # --------------------------------------------------------
    # Hardcoded passwords
    # --------------------------------------------------------

    password_pattern = re.compile(
        r"""
        (?i)
        (password|passwd|secret|api[_-]?key)
        \s*=\s*
        ["'][^"']+["']
        """,
        re.VERBOSE,
    )

    for match in password_pattern.finditer(
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