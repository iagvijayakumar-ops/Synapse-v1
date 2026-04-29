from fastapi import APIRouter
from services import session_service
from models.skill_tree import NodeState

router = APIRouter(prefix="/session", tags=["Session Progress"])

@router.get("/{session_id}/progress")
async def get_progress(session_id: str):
    """
    Returns statistics and progress for the current session.
    """
    tree = session_service.get_session(session_id)
    
    total_nodes = len(tree.nodes)
    mastered = [n.id for n in tree.nodes if n.state == NodeState.MASTERED]
    active = [n.id for n in tree.nodes if n.state == NodeState.ACTIVE]
    locked = [n.id for n in tree.nodes if n.state == NodeState.LOCKED]
    
    completion_percentage = (len(mastered) / total_nodes * 100) if total_nodes > 0 else 0
    
    return {
        "session_id": session_id,
        "topic": tree.topic,
        "total_nodes": total_nodes,
        "mastered": len(mastered),
        "active": len(active),
        "locked": len(locked),
        "completion_percentage": round(completion_percentage, 2),
        "mastered_node_ids": mastered,
        "active_node_ids": active
    }
