from pathlib import Path
import httpx
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.analyzer.analysis_engine import analyze_repository

from app.schemas.analysis import (
    AnalyzeRequest,
    AnalysisResponse,
)

from app.services.upload_service import save_and_extract_zip

from app.schemas.history import AnalysisHistoryResponse

from app.services.source_service import get_source_context

from app.services.ai_service import (
    explain_issue,
    suggest_fix,
)

from app.schemas.github import (
    GitHubAnalyzeRequest,
)

from app.services.github_service import (
    download_github_repository,
 
)

from app.database.database import (
    get_db,
    engine,
    Base
)

from app.database.models import Analysis

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="DevPilot",
    description="Developer code analysis platform",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "DevPilot API is running",
        "version": "0.1.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


# ============================================================
# SAVE ANALYSIS TO DATABASE
# ============================================================

def save_analysis(
    result: dict,
    project_path: str,
    db: Session,
):
    summary = result["summary"]

    health = result.get(
        "health",
        {}
    )

    severity = result.get(
        "severity_counts",
        {}
    )

    # --------------------------------------------------------
    # Multilingual information
    # --------------------------------------------------------

    languages = summary.get(
        "languages",
        []
    )

    language_stats = summary.get(
        "language_stats",
        {}
    )

    language_scores = health.get(
        "language_scores",
        {}
    )

    # --------------------------------------------------------
    # Project name
    # --------------------------------------------------------

    project_name = Path(
        project_path
    ).name

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    analysis = Analysis(
        project_name=project_name,
        project_path=project_path,

        # Health
        health_score=health.get(
            "score",
            0
        ),

        health_rating=health.get(
            "rating",
            "UNKNOWN"
        ),

        # Basic statistics
        total_files=summary.get(
            "total_files",
            0
        ),

        total_lines=summary.get(
            "total_lines",
            0
        ),

        total_functions=summary.get(
            "total_functions",
            0
        ),

        total_classes=summary.get(
            "total_classes",
            0
        ),

        total_imports=summary.get(
            "total_imports",
            0
        ),

        total_smells=summary.get(
            "total_smells",
            0
        ),

        total_todos=summary.get(
            "total_todos",
            0
        ),

        # Issue counts
        high_issues=severity.get(
            "HIGH",
            0
        ),

        medium_issues=severity.get(
            "MEDIUM",
            0
        ),

        low_issues=severity.get(
            "LOW",
            0
        ),

        # Multilingual information
        languages=languages,

        language_scores=language_scores,

        language_stats=language_stats,
    )

    db.add(analysis)

    db.commit()

    db.refresh(analysis)

    return analysis


# ============================================================
# ANALYZE LOCAL PROJECT
# ============================================================

@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
)
def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
):
    project_path = Path(
        request.path
    )

    # --------------------------------------------------------
    # Validate path
    # --------------------------------------------------------

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Project path does not exist",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Path must be a directory",
        )

    # --------------------------------------------------------
    # Run analysis
    # --------------------------------------------------------

    try:
        result = analyze_repository(
            str(project_path)
        )

        save_analysis(
            result,
            str(project_path),
            db,
        )

        return result

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error}",
        )


# ============================================================
# ANALYZE UPLOADED ZIP
# ============================================================

@app.post(
    "/api/v1/analyze/upload"
)
async def analyze_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported",
        )

    # --------------------------------------------------------
    # Extract and analyze
    # --------------------------------------------------------

    try:
        extract_path = save_and_extract_zip(
            file
        )

        result = analyze_repository(
            str(extract_path)
        )

        save_analysis(
            result,
            str(extract_path),
            db,
        )

        return result

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error}",
        )


# ============================================================
# SOURCE CODE CONTEXT
# ============================================================

@app.get(
    "/api/v1/source"
)
def get_source(
    file: str,
    line: int,
    context: int = 5,
):
    try:
        return get_source_context(
            file_path=file,
            line=line,
            context=context,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load source code: {error}",
        )


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@app.get(
    "/api/v1/analysis",
    response_model=list[AnalysisHistoryResponse],
)
def get_analysis_history(
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(Analysis)
        .order_by(
            Analysis.created_at.desc()
        )
        .all()
    )

    return analyses


# ============================================================
# GET SINGLE ANALYSIS
# ============================================================

@app.get(
    "/api/v1/analysis/{analysis_id}",
    response_model=AnalysisHistoryResponse,
)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return analysis


# ============================================================
# AI - EXPLAIN ISSUE
# ============================================================

@app.post(
    "/api/v1/ai/explain"
)
def explain_issue_endpoint(
    data: dict,
):
    issue = data.get(
        "issue"
    )

    source_code = data.get(
        "source_code"
    )

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    if not issue:
        raise HTTPException(
            status_code=400,
            detail="Issue data is required",
        )

    if not source_code:
        raise HTTPException(
            status_code=400,
            detail="Source code is required",
        )

    # --------------------------------------------------------
    # Generate explanation
    # --------------------------------------------------------

    try:
        explanation = explain_issue(
            issue,
            source_code,
        )

        return {
            "explanation": explanation,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI explanation failed: {error}",
        )


# ============================================================
# AI - SUGGEST FIX
# ============================================================

@app.post(
    "/api/v1/ai/fix"
)
def suggest_fix_endpoint(
    data: dict,
):
    issue = data.get(
        "issue"
    )

    source_code = data.get(
        "source_code"
    )

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    if not issue:
        raise HTTPException(
            status_code=400,
            detail="Issue data is required",
        )

    if not source_code:
        raise HTTPException(
            status_code=400,
            detail="Source code is required",
        )

    # --------------------------------------------------------
    # Generate fix
    # --------------------------------------------------------

    try:
        fix = suggest_fix(
            issue,
            source_code,
        )

        return {
            "fix": fix,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI fix generation failed: {error}",
        )
    
# ============================================================
# ANALYZE GITHUB REPOSITORY
# ============================================================

@app.post(
    "/api/v1/analyze/github",
    response_model=AnalysisResponse,
)
def analyze_github(
    request: GitHubAnalyzeRequest,
    db: Session = Depends(get_db),
):
    temp_directory = None

    try:
        # ----------------------------------------------------
        # Download repository
        # ----------------------------------------------------

        github_result = (
            download_github_repository(
                str(request.url)
            )
        )

        project_path = (
            github_result["project_path"]
        )

        temp_directory = (
            github_result["temp_directory"]
        )

        # ----------------------------------------------------
        # Analyze repository
        # ----------------------------------------------------

        result = analyze_repository(
            str(project_path)
        )

        # ----------------------------------------------------
        # Override project name with GitHub
        # repository name if necessary
        # ----------------------------------------------------

        result["summary"]["project"] = (
            github_result["repository"]
        )

        # ----------------------------------------------------
        # Save analysis
        # ----------------------------------------------------

        save_analysis(
            result,
            str(project_path),
            db,
        )

        # ----------------------------------------------------
        # Return analysis
        # ----------------------------------------------------

        return result

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except httpx.HTTPStatusError as error:
        db.rollback()

        if error.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=(
                    "GitHub repository not found. "
                    "Make sure the repository is public "
                    "and the URL is correct."
                ),
            )

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to download the GitHub repository."
            ),
        )

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"GitHub analysis failed: {error}",
        )

    