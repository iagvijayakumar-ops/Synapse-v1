from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class NodeState(str, Enum):
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"
    MASTERED = "MASTERED"

class Node(BaseModel):
    id: str
    label: str
    description: str
    state: NodeState = NodeState.LOCKED
    prerequisites: List[str] = Field(default_factory=list)
    fail_count: int = 0
    is_bridge: bool = False
    parent_node_id: Optional[str] = None

class Edge(BaseModel):
    source: str
    target: str

class SkillTree(BaseModel):
    session_id: str
    topic: str
    nodes: List[Node]
    edges: List[Edge]
