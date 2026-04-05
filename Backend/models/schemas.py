from pydantic import BaseModel
from typing import List, Dict


class Axis(BaseModel):
    name: str
    score: int
    color: str


class AnalyzeResponse(BaseModel):
    verdict: str        # "mis" | "real" | "unc"
    label: str          # "Misleading" | "Authentic" | "Uncertain"
    score: int          # 0-100
    axes: List[Axis]
    findings: List[str]
    conclusion: str
    meta: Dict[str, str]
