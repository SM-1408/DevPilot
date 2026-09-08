import ast


def find_unused_imports(tree):
    imported_names = []
    used_names = set()

    # Find imports
    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]

                imported_names.append({
                    "name": name,
                    "line": node.lineno,
                })

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue

                name = alias.asname or alias.name

                imported_names.append({
                    "name": name,
                    "line": node.lineno,
                })

    # Find names actually used in the code
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)

    # Find unused imports
    unused = []

    for imported in imported_names:
        if imported["name"] not in used_names:
            unused.append({
                "name": imported["name"],
                "line": imported["line"],
                "type": "UNUSED_IMPORT",
                "severity": "LOW",
                "message": (
                    f"Imported '{imported['name']}' "
                    f"but it is never used"
                ),
            })

    return unused