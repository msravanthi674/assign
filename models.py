from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Question(BaseModel):
    id: Optional[str] = Field(alias="_id")
    text: str
    options: List[str]
    correct_answer: str
    difficulty: float = Field(ge=0.1, le=1.0)
    topic: str
    tags: List[str]

class UserResponse(BaseModel):
    question_id: str
    answer: str
    is_correct: bool
    difficulty: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserSession(BaseModel):
    user_id: str
    ability_score: float = 0.5
    responses: List[UserResponse] = []
    completed: bool = False
    start_time: datetime = Field(default_factory=datetime.utcnow)

class StudyPlan(BaseModel):
    user_id: str
    weaknesses: List[str]
    plan: List[str]
