from pydantic import BaseModel

class AnalyzeResponse(BaseModel):
    verdict: str
    confidence: int
    explanation: str