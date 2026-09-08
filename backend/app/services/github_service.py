import shutil
import tempfile
import zipfile

from pathlib import Path
from urllib.parse import urlparse

import httpx
import time


# ============================================================
# GITHUB URL VALIDATION
# ============================================================

def parse_github_url(github_url: str):
    parsed = urlparse(github_url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            "GitHub URL must use http or https."
        )

    if parsed.netloc.lower() != "github.com":
        raise ValueError(
            "Only github.com repositories are supported."
        )

    parts = [
        part
        for part in parsed.path.strip("/").split("/")
        if part
    ]

    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL."
        )

    owner = parts[0]
    repo = parts[1]

    # Remove .git if user pasted:
    # https://github.com/user/project.git
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError(
            "Unable to determine GitHub owner and repository."
        )

    return owner, repo


# ============================================================
# CLEANUP OLD GITHUB REPOSITORIES
# ============================================================

def cleanup_old_github_repositories(
    max_age_seconds: int = 2 * 60 * 60,
):
    """
    Remove old DevPilot GitHub temporary repositories.

    Repositories are kept for a limited time so that
    Source Code inspection can still access them.
    """

    temp_root = Path(tempfile.gettempdir())

    for directory in temp_root.glob("devpilot_*"):

        if not directory.is_dir():
            continue

        try:
            age = (
                time.time()
                - directory.stat().st_mtime
            )

            if age > max_age_seconds:
                shutil.rmtree(
                    directory,
                    ignore_errors=True,
                )

        except OSError:
       
            continue


# ============================================================
# DOWNLOAD GITHUB REPOSITORY
# ============================================================

def download_github_repository(
    github_url: str,
):
    
    cleanup_old_github_repositories()
    owner, repo = parse_github_url(
        github_url
    )

    download_url = (
        f"https://github.com/"
        f"{owner}/{repo}/archive/refs/heads/main.zip"
    )

    temp_directory = Path(
        tempfile.mkdtemp(
            prefix="devpilot_"
        )
    )

    zip_path = (
        temp_directory / "repository.zip"
    )

    try:
        response = httpx.get(
            download_url,
            follow_redirects=True,
            timeout=60.0,
        )

        # ----------------------------------------------------
        # If main doesn't exist, try master
        # ----------------------------------------------------

        if response.status_code == 404:
            download_url = (
                f"https://github.com/"
                f"{owner}/{repo}/archive/refs/"
                f"heads/master.zip"
            )

            response = httpx.get(
                download_url,
                follow_redirects=True,
                timeout=60.0,
            )

        response.raise_for_status()

        zip_path.write_bytes(
            response.content
        )

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        extract_directory = (
            temp_directory / "repository"
        )

        extract_directory.mkdir(
            exist_ok=True
        )

        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as archive:

            archive.extractall(
                extract_directory
            )

        # ----------------------------------------------------
        # GitHub ZIP normally contains:
        #
        # repository-main/
        #
        # We want the actual project directory.
        # ----------------------------------------------------

        extracted_items = list(
            extract_directory.iterdir()
        )

        directories = [
            item
            for item in extracted_items
            if item.is_dir()
        ]

        if len(directories) == 1:
            project_directory = directories[0]
        else:
            project_directory = extract_directory

        return {
            "owner": owner,
            "repository": repo,
            "project_path": project_directory,
            "temp_directory": temp_directory,
        }

    except Exception:
        shutil.rmtree(
            temp_directory,
            ignore_errors=True,
        )

        raise


# ============================================================
# CLEANUP
# ============================================================

def cleanup_github_repository(
    temp_directory: Path,
):
    shutil.rmtree(
        temp_directory,
        ignore_errors=True,
    )