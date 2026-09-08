from pydantic import BaseModel
from typing import Any


class AnalysisHistoryResponse(BaseModel):
    id: int

    project_name: str
    project_path: str

    health_score: int
    health_rating: str

    total_files: int
    total_lines: int
    total_functions: int
    total_classes: int
    total_imports: int
    total_smells: int
    total_todos: int

    high_issues: int
    medium_issues: int
    low_issues: int

    languages: list[str] | None = None
    language_scores: dict[str, Any] | None = None
    language_stats: dict[str, Any] | None = None

    created_at: Any

    class Config:
        from_attributes = True