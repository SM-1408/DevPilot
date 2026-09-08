from app.services.ai_service import ask_ollama


result = ask_ollama(
    "Explain cyclomatic complexity in 2 simple sentences."
)

print(result)