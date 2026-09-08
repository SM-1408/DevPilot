from pathlib import Path

from app.analyzer.javascript_analyzer import (
    find_classes,
    find_functions,
    find_imports,
    find_todos,
    calculate_function_complexity,
    complexity_level,
    find_function_smells,
    find_security_issues,
)


# ============================================================
# TYPESCRIPT ANALYZER
# ============================================================

def analyze_typescript_file(file_path: str):

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
        "language": "TypeScript",
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