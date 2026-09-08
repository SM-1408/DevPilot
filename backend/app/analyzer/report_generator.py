def generate_report(analysis_result):
    summary = analysis_result["summary"]
    issues = analysis_result["issues"]
    health = analysis_result["health"]

    # ============================================================
    # ISSUE COUNTS
    # ============================================================

    severity_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    issue_type_counts = {}

    for issue in issues:
        issue_type = issue.get("type", "UNKNOWN")

        issue_type_counts[issue_type] = (
            issue_type_counts.get(issue_type, 0) + 1
        )

        severity = issue.get("severity")

        if severity in severity_counts:
            severity_counts[severity] += 1

    # ============================================================
    # LANGUAGE ISSUE COUNTS
    # ============================================================

    language_issue_counts = {}

    for file_result in analysis_result.get("files", []):
        language = file_result.get("language")

        if not language:
            continue

        if language not in language_issue_counts:
            language_issue_counts[language] = {
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "total": 0,
            }

        file_path = file_result["file"]

        for issue in issues:
            if issue.get("file") != file_path:
                continue

            severity = issue.get("severity")

            if severity in language_issue_counts[language]:
                language_issue_counts[language][severity] += 1

            language_issue_counts[language]["total"] += 1

    # ============================================================
    # WORST FUNCTIONS
    # ============================================================

    functions = []

    for file_result in analysis_result["files"]:
        for function in file_result.get("functions", []):

            functions.append({
                "file": file_result["file"],
                "language": file_result.get(
                    "language",
                    "Unknown"
                ),
                "name": function["name"],
                "line": function["line"],
                "complexity": function["complexity"],
                "level": function["level"],
                "smells": len(
                    function.get("smells", [])
                ),
            })

    functions.sort(
        key=lambda function: (
            function["complexity"],
            function["smells"],
        ),
        reverse=True,
    )

    # ============================================================
    # WORST FILES
    # ============================================================

    files = []

    for file_result in analysis_result["files"]:

        file_path = file_result["file"]

        file_issues = [
            issue
            for issue in issues
            if issue.get("file") == file_path
        ]

        files.append({
            "file": file_path,
            "language": file_result.get(
                "language",
                "Unknown"
            ),
            "lines": file_result.get("lines", 0),
            "functions": len(
                file_result.get("functions", [])
            ),
            "classes": len(
                file_result.get("classes", [])
            ),
            "issues": len(file_issues),
        })

    files.sort(
        key=lambda file: file["issues"],
        reverse=True,
    )

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================

    recommendations = []

    if severity_counts["HIGH"] > 0:
        recommendations.append(
            "Fix high-severity issues first."
        )

    if summary.get("total_smells", 0) > 0:
        recommendations.append(
            "Refactor functions with code smells."
        )

    if summary.get("total_todos", 0) > 0:
        recommendations.append(
            "Review outstanding TODO and FIXME items."
        )

    if summary.get("total_lines", 0) > 1000:
        recommendations.append(
            "Consider splitting large modules."
        )

    if summary.get("language_count", 0) > 1:
        recommendations.append(
            "Review code quality across all detected languages."
        )

    if not recommendations:
        recommendations.append(
            "No major issues detected."
        )

    # ============================================================
    # FINAL REPORT
    # ============================================================

    return {
        "health": health,

        "summary": summary,

        "severity_counts": severity_counts,

        "issue_type_counts": issue_type_counts,

        "language_issue_counts": language_issue_counts,

        "worst_functions": functions[:10],

        "worst_files": files[:10],

        "recommendations": recommendations,

        "issues": issues,
    }