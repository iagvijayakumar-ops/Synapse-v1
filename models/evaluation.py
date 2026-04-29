from typing import Optional, List
from pydantic import BaseModel, Field
from .skill_tree import Node

class EvalRequest(BaseModel):
    session_id: str
    node_id: str
    selected_option_id: str
    correct_option_id: str
    question: str
    node_label: str
    reasoning: str = Field(..., min_length=10)

class EvalResult(BaseModel):
    correct: bool
    reasoning_score: int
    reasoning_feedback: str
    nodes_unlocked: List[str]
    bridge_node_created: Optional[Node] = None
    message: str
