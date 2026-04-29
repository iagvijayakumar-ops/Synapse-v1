from typing import List
from pydantic import BaseModel, Field

class QuizOption(BaseModel):
    id: str
    text: str

class Quiz(BaseModel):
    question: str
    options: List[QuizOption]
    correct_option_id: str
    explanation: str

class MicroLesson(BaseModel):
    node_id: str
    title: str
    content: str
    quiz: Quiz
