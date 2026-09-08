from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    JSON
)

from app.database.database import Base


class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_name = Column(
        String(255),
        nullable=False
    )

    project_path = Column(
        Text,
        nullable=False
    )

    health_score = Column(
        Integer,
        nullable=False
    )

    health_rating = Column(
        String(50),
        nullable=False
    )

    languages = Column(
        JSON,
        nullable=True
    )

    language_scores = Column(
        JSON,
        nullable=True
    )

    language_stats = Column(
        JSON,
        nullable=True
    )

    total_files = Column(
        Integer,
        default=0
    )

    total_lines = Column(
        Integer,
        default=0
    )

    total_functions = Column(
        Integer,
        default=0
    )

    total_classes = Column(
        Integer,
        default=0
    )

    total_imports = Column(
        Integer,
        default=0
    )

    total_smells = Column(
        Integer,
        default=0
    )

    total_todos = Column(
        Integer,
        default=0
    )

    high_issues = Column(
        Integer,
        default=0
    )

    medium_issues = Column(
        Integer,
        default=0
    )

    low_issues = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )