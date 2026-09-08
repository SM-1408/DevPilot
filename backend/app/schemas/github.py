from pydantic import BaseModel, HttpUrl


class GitHubAnalyzeRequest(BaseModel):
    url: HttpUrl