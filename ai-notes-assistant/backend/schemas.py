from pydantic import BaseModel
from typing import List


class NotesIn(BaseModel):
    text: str


class NotesAnalysisOut(BaseModel):
    summary: str
    todos: List[str]
