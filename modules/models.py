from pydantic import BaseModel
from typing import List

class Student(BaseModel):
    id: int
    name: str
    communities: List[str]
    skills: List[str]
    interests: List[str]
    interactions: int
    teamwork: int
