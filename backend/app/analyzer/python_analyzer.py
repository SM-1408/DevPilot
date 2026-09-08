import ast
from pathlib import Path
from app.analyzer.project_scanner import find_python_files
from app.analyzer.code_smells import (
    analyze_function_smells,
    analyze_security_smells,
    find_todos
)
from app.analyzer.duplicate_detector import find_duplicate_code  
from app.analyzer.import_detector import find_unused_imports   
from app.analyzer.security_detector import find_security_issues

class ComplexityVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def calculate_complexity(node):
    visitor = ComplexityVisitor()
    visitor.visit(node)

    return visitor.complexity


def complexity_level(complexity):

    if complexity <= 5:
        return "LOW"

    if complexity <= 10:
        return "MEDIUM"

    if complexity <= 20:
        return "HIGH"

    return "VERY HIGH"


def analyze_python_file(file_path: str):

    path = Path(file_path)

    source_code = path.read_text(encoding="utf-8")

    tree = ast.parse(source_code)

    security_smells = analyze_security_smells(tree)

    duplicates = []

    tree = ast.parse(source_code)

    security_issues = find_security_issues(tree)

    unused_imports = find_unused_imports(tree)

    functions = []
    classes = []
    imports = []

    # Find TODO and FIXME comments
    todos = find_todos(source_code)

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            complexity = calculate_complexity(node)

            smells = analyze_function_smells(node)

            functions.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "level": complexity_level(complexity),
                "smells": smells
            })

        elif isinstance(node, ast.ClassDef):

            classes.append(node.name)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):

            imports.append(ast.unparse(node))

    lines = len(source_code.splitlines())

    return {
    "file": str(path),
    "lines": lines,
    "functions": functions,
    "classes": classes,
    "imports": imports,
    "todos": todos,
    "security_smells": security_smells,
    "duplicates": duplicates,
    "unused_imports": unused_imports,
    "security_issues": security_issues,      
}


def analyze_project(project_path: str):

    project = Path(project_path)

    python_files = find_python_files(project_path)

    files = []

    total_lines = 0
    total_functions = 0
    total_classes = 0
    total_imports = 0

    for file_path in python_files:

        try:

            result = analyze_python_file(str(file_path))

            files.append(result)

            total_lines += result["lines"]
            total_functions += len(result["functions"])
            total_classes += len(result["classes"])
            total_imports += len(result["imports"])

        except (SyntaxError, UnicodeDecodeError) as error:

            print(f"Skipping {file_path}: {error}")

    return {
        "project": project.name,
        "total_files": len(files),
        "total_lines": total_lines,
        "total_functions": total_functions,
        "total_classes": total_classes,
        "total_imports": total_imports,
        "files": files,
    }