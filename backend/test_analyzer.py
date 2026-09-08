from app.analyzer.analysis_engine import analyze_repository


result = analyze_repository(".")


print("\n======================")
print("     DEV PILOT")
print("======================")


health = result["health"]

print("\nHEALTH")
print("----------------------")
print(f"Score:  {health['score']}/100")
print(f"Rating: {health['rating']}")


summary = result["summary"]

print("\nSUMMARY")
print("----------------------")
print(f"Files:      {summary['total_files']}")
print(f"Lines:      {summary['total_lines']}")
print(f"Functions:  {summary['total_functions']}")
print(f"Classes:    {summary['total_classes']}")
print(f"Imports:    {summary['total_imports']}")
print(f"Smells:     {summary['total_smells']}")
print(f"TODOs:      {summary['total_todos']}")


print("\nSEVERITY")
print("----------------------")

for severity, count in result["severity_counts"].items():
    print(f"{severity}: {count}")


print("\nWORST FUNCTIONS")
print("----------------------")

for function in result["worst_functions"]:

    print(
        f"{function['name']} "
        f"| Complexity: {function['complexity']} "
        f"| Smells: {function['smells']}"
    )


print("\nWORST FILES")
print("----------------------")

for file in result["worst_files"]:

    print(
        f"{file['file']} "
        f"| Issues: {file['issues']} "
        f"| Lines: {file['lines']}"
    )


print("\nRECOMMENDATIONS")
print("----------------------")

for recommendation in result["recommendations"]:
    print(f"- {recommendation}")