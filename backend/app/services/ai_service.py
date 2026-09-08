import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def ask_ollama(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the generated response.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "Ollama returned an empty response."
        )

    except requests.exceptions.ConnectionError:
        return (
            "Unable to connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        return (
            "Ollama took too long to respond."
        )

    except requests.exceptions.RequestException as error:
        return (
            f"Ollama request failed: {error}"
        )

    except Exception as error:
        return (
            f"Unexpected AI service error: {error}"
        )


# =========================================================
# EXPLAIN ISSUE
# =========================================================

def explain_issue(issue: dict, source_code: str) -> str:
    """
    Explain an issue detected by DevPilot.
    """

    issue_type = issue.get(
        "type",
        "UNKNOWN"
    )

    severity = issue.get(
        "severity",
        "UNKNOWN"
    )

    message = issue.get(
        "message",
        "No message available."
    )

    prompt = (
        "You are an expert Python code reviewer "
        "working inside a developer code analysis "
        "platform called DevPilot.\n\n"

        "Analyze the following issue found in "
        "a Python project.\n\n"

        f"Issue Type: {issue_type}\n"
        f"Severity: {severity}\n"
        f"Issue Message: {message}\n\n"

        "Source Code:\n"
        "```python\n"
        f"{source_code}\n"
        "```\n\n"

        "Provide a clear developer-friendly explanation.\n\n"

        "Explain:\n"
        "1. What is wrong?\n"
        "2. Why is it a problem?\n"
        "3. How can it be fixed?\n"
        "4. Show corrected code if appropriate.\n\n"

        "Keep the response practical and concise.\n"
        "Do not invent problems that are not present "
        "in the source code."
    )

    return ask_ollama(prompt)


# =========================================================
# SUGGEST FIX
# =========================================================

def suggest_fix(issue: dict, source_code: str) -> str:
    """
    Generate an AI-powered fix suggestion
    for a detected issue.
    """

    issue_type = issue.get(
        "type",
        "UNKNOWN"
    )

    severity = issue.get(
        "severity",
        "UNKNOWN"
    )

    message = issue.get(
        "message",
        "No message available."
    )

    prompt = (
        "You are an expert Python developer "
        "working inside a code analysis platform "
        "called DevPilot.\n\n"

        "A static analyzer detected the following "
        "issue in Python code.\n\n"

        f"Issue Type: {issue_type}\n"
        f"Severity: {severity}\n"
        f"Issue Message: {message}\n\n"

        "Source Code:\n"
        "```python\n"
        f"{source_code}\n"
        "```\n\n"

        "Your task is to suggest a practical fix.\n\n"

        "Provide the response using exactly these sections:\n\n"

        "PROBLEM\n"
        "Briefly explain the problem.\n\n"

        "WHY IT MATTERS\n"
        "Explain the impact of this issue.\n\n"

        "SUGGESTED FIX\n"
        "Explain what should be changed.\n\n"

        "FIXED CODE\n"
        "Provide the corrected Python code when "
        "a code change is appropriate.\n\n"

        "IMPORTANT:\n"
        "- Only fix the detected issue.\n"
        "- Do not rewrite unrelated code.\n"
        "- Do not invent problems.\n"
        "- Preserve the original behavior whenever possible.\n"
        "- Keep the solution practical.\n"
    )

    return ask_ollama(prompt)