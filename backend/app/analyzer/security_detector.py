import ast


def find_security_issues(tree):
    issues = []

    for node in ast.walk(tree):

        # --------------------------------
        # eval()
        # --------------------------------
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "eval":
                    issues.append({
                        "line": node.lineno,
                        "type": "DANGEROUS_EVAL",
                        "severity": "HIGH",
                        "message": "Use of eval() can execute arbitrary code."
                    })

                # --------------------------------
                # exec()
                # --------------------------------
                elif node.func.id == "exec":
                    issues.append({
                        "line": node.lineno,
                        "type": "DANGEROUS_EXEC",
                        "severity": "HIGH",
                        "message": "Use of exec() can execute arbitrary code."
                    })

        # --------------------------------
        # Hardcoded passwords / API keys
        # --------------------------------
        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    name = target.id.lower()

                    sensitive_names = [
                        "password",
                        "passwd",
                        "secret",
                        "api_key",
                        "apikey",
                        "token"
                    ]

                    if any(word in name for word in sensitive_names):

                        if isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, str):
                                issues.append({
                                    "line": node.lineno,
                                    "type": "HARDCODED_SECRET",
                                    "severity": "HIGH",
                                    "message": (
                                        f"Possible hardcoded secret in "
                                        f"'{target.id}'."
                                    )
                                })

    return issues