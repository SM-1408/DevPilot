from pathlib import Path


# ============================================================
# DIRECTORIES TO IGNORE
# ============================================================

IGNORED_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    "storage",
}


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}


# ============================================================
# VALIDATE PROJECT
# ============================================================

def validate_project(project_path: str) -> Path:
    project = Path(project_path)

    if not project.exists():
        raise FileNotFoundError(
            f"Project path does not exist: {project_path}"
        )

    if not project.is_dir():
        raise NotADirectoryError(
            f"Project path is not a directory: {project_path}"
        )

    return project


# ============================================================
# CHECK WHETHER FILE SHOULD BE IGNORED
# ============================================================

def is_ignored(file_path: Path) -> bool:
    return any(
        directory in IGNORED_DIRECTORIES
        for directory in file_path.parts
    )


# ============================================================
# FIND ALL SUPPORTED SOURCE FILES
# ============================================================

def find_source_files(project_path: str):
    project = validate_project(project_path)

    source_files = []

    for file_path in project.rglob("*"):

        if not file_path.is_file():
            continue

        if is_ignored(file_path):
            continue

        if file_path.suffix.lower() not in LANGUAGE_EXTENSIONS:
            continue

        source_files.append(file_path)

    return source_files


# ============================================================
# DETECT LANGUAGE OF A FILE
# ============================================================

def detect_file_language(file_path: Path) -> str | None:
    return LANGUAGE_EXTENSIONS.get(file_path.suffix.lower())


# ============================================================
# DETECT ALL LANGUAGES USED BY PROJECT
# ============================================================

def detect_project_languages(project_path: str):
    source_files = find_source_files(project_path)

    languages = set()

    for file_path in source_files:
        language = detect_file_language(file_path)

        if language:
            languages.add(language)

    return sorted(languages)


# ============================================================
# GROUP FILES BY LANGUAGE
# ============================================================

def get_files_by_language(project_path: str):
    source_files = find_source_files(project_path)

    files_by_language = {
        "Python": [],
        "Java": [],
        "JavaScript": [],
        "TypeScript": [],
    }

    for file_path in source_files:
        language = detect_file_language(file_path)

        if language:
            files_by_language[language].append(file_path)

    return files_by_language


# ============================================================
# PROJECT SCAN
# ============================================================

def scan_project(project_path: str):
    source_files = find_source_files(project_path)

    files_by_language = {
        "Python": [],
        "Java": [],
        "JavaScript": [],
        "TypeScript": [],
    }

    for file_path in source_files:
        language = detect_file_language(file_path)

        if language:
            files_by_language[language].append(file_path)

    detected_languages = sorted(
        language
        for language, files in files_by_language.items()
        if files
    )

    return {
        "project_path": str(Path(project_path).resolve()),
        "languages": detected_languages,
        "language_count": len(detected_languages),
        "total_files": len(source_files),
        "files_by_language": files_by_language,
    }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def find_python_files(project_path: str):
    project = validate_project(project_path)

    python_files = []

    for file_path in project.rglob("*.py"):

        if is_ignored(file_path):
            continue

        python_files.append(file_path)

    return python_files