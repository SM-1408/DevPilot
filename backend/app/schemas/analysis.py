from pydantic import BaseModel
from typing import Any


class AnalyzeRequest(BaseModel):
    path: str


class HealthBreakdown(BaseModel):
    high_issues: int
    medium_issues: int
    low_issues: int
    complexity_issues: int
    security_issues: int


class LanguageHealth(BaseModel):
    score: int
    rating: str
    breakdown: HealthBreakdown


class HealthResponse(BaseModel):
    score: int
    rating: str
    breakdown: HealthBreakdown
    language_scores: dict[str, LanguageHealth]


class AnalysisResponse(BaseModel):
    health: HealthResponse

    summary: dict[str, Any]

    severity_counts: dict[str, int]

    worst_functions: list[dict[str, Any]]

    worst_files: list[dict[str, Any]]

    recommendations: list[str]

    issues: list[dict[str, Any]]

    issue_type_counts: dict[str, int]