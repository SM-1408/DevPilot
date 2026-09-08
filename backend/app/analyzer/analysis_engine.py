from pathlib import Path

from app.analyzer.project_scanner import (
    scan_project,
    detect_file_language,
)

from app.analyzer.python_analyzer import analyze_python_file

from app.analyzer.issue_detector import collect_issues
from app.analyzer.health_score import calculate_health_score
from app.analyzer.report_generator import generate_report
from app.analyzer.duplicate_detector import find_duplicate_code
from app.analyzer.java_analyzer import analyze_java_file
from app.analyzer.javascript_analyzer import (
    analyze_javascript_file
)

from app.analyzer.typescript_analyzer import (
    analyze_typescript_file
)


# ============================================================
# LANGUAGE ANALYZER DISPATCHER
# ============================================================

def analyze_source_file(
    file_path: Path,
    language: str
):

    if language == "Python":
        return analyze_python_file(
            str(file_path)
        )

    if language == "Java":
        return analyze_java_file(
            str(file_path)
        )

    if language == "JavaScript":
        return analyze_javascript_file(
            str(file_path)
        )

    if language == "TypeScript":
        return analyze_typescript_file(
            str(file_path)
        )

    raise NotImplementedError(
        f"No analyzer implemented for {language}"
    )


# ============================================================
# MAIN REPOSITORY ANALYZER
# ============================================================

def analyze_repository(project_path: str):

    project = Path(project_path)

    # --------------------------------------------------------
    # SCAN PROJECT
    # --------------------------------------------------------

    scan = scan_project(project_path)

    files = []

    # --------------------------------------------------------
    # PROJECT STATISTICS
    # --------------------------------------------------------

    total_lines = 0
    total_functions = 0
    total_classes = 0
    total_imports = 0
    total_smells = 0
    total_todos = 0

    # --------------------------------------------------------
    # LANGUAGE STATISTICS
    # --------------------------------------------------------

    language_stats = {}

    for language in scan["languages"]:
        language_stats[language] = {
            "files": 0,
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "smells": 0,
            "todos": 0,
        }

    # --------------------------------------------------------
    # ANALYZE SOURCE FILES
    # --------------------------------------------------------

    for source_files in scan["files_by_language"].values():
        for source_file in source_files:

            language = detect_file_language(source_file)

            if not language:
                continue

            try:

                result = analyze_source_file(
                    source_file,
                    language
                )

                # ------------------------------------------------
                # Add language information
                # ------------------------------------------------

                result["language"] = language

                files.append(result)

                # ------------------------------------------------
                # Global statistics
                # ------------------------------------------------

                lines = result.get("lines", 0)

                functions = result.get(
                    "functions",
                    []
                )

                classes = result.get(
                    "classes",
                    []
                )

                imports = result.get(
                    "imports",
                    []
                )

                todos = result.get(
                    "todos",
                    []
                )

                total_lines += lines
                total_functions += len(functions)
                total_classes += len(classes)
                total_imports += len(imports)
                total_todos += len(todos)

                # ------------------------------------------------
                # Count smells
                # ------------------------------------------------

                file_smells = 0

                for function in functions:

                    file_smells += len(
                        function.get(
                            "smells",
                            []
                        )
                    )

                total_smells += file_smells

                # ------------------------------------------------
                # Language statistics
                # ------------------------------------------------

                stats = language_stats[language]

                stats["files"] += 1
                stats["lines"] += lines
                stats["functions"] += len(functions)
                stats["classes"] += len(classes)
                stats["imports"] += len(imports)
                stats["smells"] += file_smells
                stats["todos"] += len(todos)

            except (
                SyntaxError,
                UnicodeDecodeError,
                NotImplementedError,
            ) as error:

                print(
                    f"Skipping {source_file}: {error}"
                )

    # ============================================================
    # DUPLICATE CODE
    # ============================================================

    # For now duplicate detection remains Python-based.
    # We will make this multilingual later.

    python_files = [
        file_result["file"]
        for file_result in files
        if file_result.get("language") == "Python"
    ]

    duplicates = find_duplicate_code(
        python_files
    )

    # ============================================================
    # BUILD ANALYSIS RESULT
    # ============================================================

    analysis_result = {

        "summary": {

            "project": project.name,

            "total_files": len(files),

            "total_lines": total_lines,

            "total_functions": total_functions,

            "total_classes": total_classes,

            "total_imports": total_imports,

            "total_smells": total_smells,

            "total_todos": total_todos,

            # --------------------------------------------
            # MULTILINGUAL INFORMATION
            # --------------------------------------------

            "languages": scan["languages"],

            "language_count": scan["language_count"],

            "language_stats": language_stats,
        },

        "issues": [],

        "files": files,

        "duplicates": duplicates,
    }

    # ============================================================
    # COLLECT ISSUES
    # ============================================================

    issues = collect_issues(
        analysis_result
    )

    analysis_result["issues"] = issues

    # ============================================================
    # HEALTH SCORE
    # ============================================================

    health = calculate_health_score(
        analysis_result
    )

    analysis_result["health"] = health

    # ============================================================
    # GENERATE REPORT
    # ============================================================

    report = generate_report(
        analysis_result
    )

    return report