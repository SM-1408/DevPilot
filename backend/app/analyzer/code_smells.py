import ast


def get_function_length(node):
    return node.end_lineno - node.lineno + 1


def get_parameter_count(node):
    return len(node.args.args)


def get_max_nesting(node):
    max_depth = 0

    def visit(current_node, depth):

        nonlocal max_depth

        if isinstance(
            current_node,
            (ast.If, ast.For, ast.While, ast.With, ast.Try)
        ):
            depth += 1
            max_depth = max(max_depth, depth)

        for child in ast.iter_child_nodes(current_node):
            visit(child, depth)

    visit(node, 0)

    return max_depth


def analyze_function_smells(node):

    smells = []

    length = get_function_length(node)

    if length > 50:
        smells.append({
            "type": "LONG_FUNCTION",
            "message": f"Function contains {length} lines",
            "severity": "HIGH"
        })

    parameter_count = get_parameter_count(node)

    if parameter_count > 5:
        smells.append({
            "type": "TOO_MANY_PARAMETERS",
            "message": f"Function has {parameter_count} parameters",
            "severity": "MEDIUM"
        })

    nesting = get_max_nesting(node)

    if nesting > 3:
        smells.append({
            "type": "DEEP_NESTING",
            "message": f"Maximum nesting depth is {nesting}",
            "severity": "HIGH"
        })

    return smells

def analyze_security_smells(tree):
    smells = []

    for node in ast.walk(tree):

        # Dangerous eval()
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "eval"
        ):
            smells.append({
                "type": "DANGEROUS_EVAL",
                "line": node.lineno,
                "message": "Use of eval() can execute arbitrary code",
                "severity": "HIGH"
            })

        # Dangerous exec()
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "exec"
        ):
            smells.append({
                "type": "DANGEROUS_EXEC",
                "line": node.lineno,
                "message": "Use of exec() can execute arbitrary code",
                "severity": "HIGH"
            })

        # Debug print
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            smells.append({
                "type": "DEBUG_PRINT",
                "line": node.lineno,
                "message": "print() statement may be leftover debugging code",
                "severity": "LOW"
            })

    return smells

def find_todos(source_code):

    todos = []

    for line_number, line in enumerate(
        source_code.splitlines(),
        start=1
    ):

        if "TODO" in line:
            todos.append({
                "type": "TODO",
                "line": line_number,
                "message": line.strip()
            })

        if "FIXME" in line:
            todos.append({
                "type": "FIXME",
                "line": line_number,
                "message": line.strip()
            })

    return todos