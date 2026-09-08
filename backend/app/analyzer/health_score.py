# app/analyzer/health_score.py


def get_rating(score):
    if score >= 90:
        return "EXCELLENT"

    if score >= 75:
        return "GOOD"

    if score >= 60:
        return "FAIR"

    if score >= 40:
        return "POOR"

    return "CRITICAL"


def calculate_score(issues):
    """
    Calculate a health score for a collection of issues.

    The score uses bounded penalties so that a large number of
    low-severity issues does not automatically reduce the project
    health to zero.
    """

    high_issues = sum(
        1
        for issue in issues
        if issue.get("severity") == "HIGH"
    )

    medium_issues = sum(
        1
        for issue in issues
        if issue.get("severity") == "MEDIUM"
    )

    low_issues = sum(
        1
        for issue in issues
        if issue.get("severity") == "LOW"
    )

    complexity_issues = sum(
        1
        for issue in issues
        if issue.get("type") == "HIGH_COMPLEXITY"
    )

    security_issues = sum(
        1
        for issue in issues
        if issue.get("type") in (
            "DANGEROUS_EVAL",
            "DANGEROUS_EXEC",
            "PROCESS_EXECUTION",
            "HARDCODED_SECRET",
        )
    )

    # ============================================================
    # BOUNDED PENALTIES
    # ============================================================

    # High severity:
    # Strong impact, but capped.
    high_penalty = min(high_issues * 1.2, 25)

    # Medium severity:
    # Moderate impact, capped.
    medium_penalty = min(medium_issues * 0.5, 10)

    # Low severity:
    # Small impact, heavily capped.
    low_penalty = min(low_issues * 0.1, 5)

    # Complexity:
    # Important, but should not dominate the score.
    complexity_penalty = min(complexity_issues * 1.0, 10)

    # Security:
    # Security problems are treated separately because
    # they are more dangerous than normal code-quality issues.
    security_penalty = min(security_issues * 5.0, 30)

    # ============================================================
    # FINAL SCORE
    # ============================================================

    total_penalty = (
        high_penalty
        + medium_penalty
        + low_penalty
        + complexity_penalty
        + security_penalty
    )

    score = 100 - total_penalty

    score = max(0, min(100, score))

    return {
        "score": round(score),
        "rating": get_rating(score),
        "breakdown": {
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "complexity_issues": complexity_issues,
            "security_issues": security_issues,
        },
    }

def calculate_health_score(analysis_result):
    """
    Calculate both:

    1. Overall project health
    2. Individual language health

    A project can contain:
        Python
        Java
        JavaScript
        TypeScript

    The overall score is calculated from ALL project issues.
    Language scores are calculated independently.
    """

    issues = analysis_result.get("issues", [])
    files = analysis_result.get("files", [])

    # ============================================================
    # OVERALL PROJECT SCORE
    # ============================================================

    overall = calculate_score(issues)

    # ============================================================
    # LANGUAGE SCORES
    # ============================================================

    language_issues = {}

    for file_result in files:

        language = file_result.get("language")

        if not language:
            continue

        if language not in language_issues:
            language_issues[language] = []

        file_path = file_result.get("file")

        for issue in issues:

            if issue.get("file") == file_path:
                language_issues[language].append(issue)

    language_scores = {}

    for language, lang_issues in language_issues.items():

        language_result = calculate_score(lang_issues)

        language_scores[language] = {
            "score": language_result["score"],
            "rating": language_result["rating"],
            "breakdown": language_result["breakdown"],
        }

    # ============================================================
    # FINAL HEALTH RESULT
    # ============================================================

    return {
        "score": overall["score"],
        "rating": overall["rating"],
        "breakdown": overall["breakdown"],
        "language_scores": language_scores,
    }