def collect_issues(analysis_result):
    issues = []

    # =====================================================
    # FILE-LEVEL ANALYSIS
    # =====================================================

    for file_result in analysis_result.get("files", []):

        # -------------------------------------------------
        # File path
        # -------------------------------------------------

        file_path = file_result["file"]

        # -------------------------------------------------
        # File-level security smells
        # -------------------------------------------------

        for smell in file_result.get("security_smells", []):
            issues.append({
                "file": file_path,
                "line": smell["line"],
                "type": smell["type"],
                "severity": smell["severity"],
                "message": smell["message"],
            })

        # -------------------------------------------------
        # Function-level issues
        # -------------------------------------------------

        for function in file_result.get("functions", []):

            # ---------------------------------------------
            # Function code smells
            # ---------------------------------------------

            for smell in function.get("smells", []):
                issues.append({
                    "file": file_path,
                    "function": function["name"],
                    "line": smell.get(
                        "line",
                        function["line"]
                    ),
                    "type": smell["type"],
                    "severity": smell["severity"],
                    "message": smell["message"],
                })

            # ---------------------------------------------
            # High complexity
            # ---------------------------------------------

            if function["complexity"] > 10:
                issues.append({
                    "file": file_path,
                    "function": function["name"],
                    "line": function["line"],
                    "type": "HIGH_COMPLEXITY",
                    "severity": "HIGH",
                    "message": (
                        f"Cyclomatic complexity is "
                        f"{function['complexity']}"
                    ),
                })

        # -------------------------------------------------
        # TODO / FIXME issues
        # -------------------------------------------------

        for todo in file_result.get("todos", []):
            issues.append({
                "file": file_path,
                "line": todo["line"],
                "type": todo["type"],
                "severity": "LOW",
                "message": todo["message"],
            })

        # -------------------------------------------------
        # Unused import issues
        # -------------------------------------------------

        for unused_import in file_result.get(
            "unused_imports",
            []
        ):
            issues.append({
                "file": file_path,
                "line": unused_import["line"],
                "type": unused_import["type"],
                "severity": unused_import["severity"],
                "message": unused_import["message"],
            })

        # -------------------------------------------------
        # Security issues
        # -------------------------------------------------

        for security_issue in file_result.get(
            "security_issues",
            []
        ):
            issues.append({
                "file": file_path,
                "line": security_issue["line"],
                "type": security_issue["type"],
                "severity": security_issue["severity"],
                "message": security_issue["message"],
            })

    # =====================================================
    # REPOSITORY-LEVEL DUPLICATE CODE
    # =====================================================

    for duplicate in analysis_result.get(
        "duplicates",
        []
    ):
        issues.append({
            "file": duplicate["file1"],
            "function": duplicate["function1"],
            "line": duplicate["line1"],
            "type": duplicate["type"],
            "severity": duplicate["severity"],
            "message": duplicate["message"],
        })

    # =====================================================
    # RETURN ALL ISSUES
    # =====================================================

    return issues