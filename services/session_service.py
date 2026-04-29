import threading
from typing import Dict, Optional
from fastapi import HTTPException
from models.skill_tree import SkillTree, Node

# In-memory storage
sessions: Dict[str, SkillTree] = {}
lock = threading.Lock()

def create_session(tree: SkillTree) -> str:
    """
    Stores a new SkillTree session.
    """
    with lock:
        sessions[tree.session_id] = tree
    return tree.session_id

def get_session(session_id: str) -> SkillTree:
    """
    Retrieves a session by ID or raises 404.
    """
    with lock:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return sessions[session_id]

def update_session(session_id: str, tree: SkillTree) -> None:
    """
    Updates an existing session.
    """
    with lock:
        sessions[session_id] = tree

def delete_session(session_id: str) -> None:
    """
    Removes a session.
    """
    with lock:
        if session_id in sessions:
            del sessions[session_id]

def get_node(tree: SkillTree, node_id: str) -> Node:
    """
    Finds a node within a tree or raises 404.
    """
    for node in tree.nodes:
        if node.id == node_id:
            return node
    raise HTTPException(status_code=404, detail="Node not found in this session")
