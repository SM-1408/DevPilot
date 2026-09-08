import ast
from pathlib import Path


def normalize_code(node):
    """
    Convert an AST node into normalized code.

    Variable names and formatting differences are removed
    so structurally similar code can be detected.
    """

    if isinstance(node, ast.Name):
        return "NAME"

    if isinstance(node, ast.Constant):
        return "CONSTANT"

    try:
        return ast.dump(node, annotate_fields=False)
    except Exception:
        return str(node)


def get_function_signature(node):
    """
    Create a normalized representation of a function.
    """

    body = []

    for statement in node.body:
        body.append(normalize_code(statement))

    return "\n".join(body)


def find_duplicate_code(file_paths):
    """
    Find duplicate or highly similar functions across Python files.

    Returns a list of duplicate function pairs.
    """

    functions = []

    for file_path in file_paths:
        path = Path(file_path)

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)

        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                functions.append({
                    "file": str(path),
                    "name": node.name,
                    "line": node.lineno,
                    "signature": get_function_signature(node),
                })

    duplicates = []

    for i in range(len(functions)):

        for j in range(i + 1, len(functions)):

            first = functions[i]
            second = functions[j]

            if not first["signature"]:
                continue

            if first["signature"] == second["signature"]:

                duplicates.append({
                    "file1": first["file"],
                    "function1": first["name"],
                    "line1": first["line"],

                    "file2": second["file"],
                    "function2": second["name"],
                    "line2": second["line"],

                    "type": "DUPLICATE_CODE",
                    "severity": "MEDIUM",

                    "message": (
                        f"Function '{first['name']}' in "
                        f"{first['file']} appears to duplicate "
                        f"function '{second['name']}' in "
                        f"{second['file']}."
                    ),
                })

    return duplicates