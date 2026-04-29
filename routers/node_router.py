from fastapi import APIRouter, HTTPException
from models.lesson import MicroLesson
from models.evaluation import EvalRequest, EvalResult
from models.skill_tree import NodeState
from services import ai_service, graph_service, session_service

router = APIRouter(prefix="/node", tags=["Node Operations"])

@router.get("/{session_id}/{node_id}/lesson", response_model=MicroLesson)
async def get_lesson(session_id: str, node_id: str):
    """
    Generates a micro-lesson and quiz for an active node.
    """
    tree = session_service.get_session(session_id)
    node = session_service.get_node(tree, node_id)
    
    if node.state == NodeState.LOCKED:
        raise HTTPException(status_code=403, detail="Node is locked. Complete prerequisites first.")
    
    if node.state == NodeState.MASTERED:
        # We still allow viewing, but maybe return a special message or flag?
        # User requested 200 with message "already mastered" but we must return MicroLesson model.
        # We'll just generate it.
        pass
        
    lesson_data = await ai_service.generate_micro_lesson(node.label, node.description, tree.topic)
    return MicroLesson(node_id=node_id, **lesson_data)

@router.post("/{session_id}/{node_id}/evaluate", response_model=EvalResult)
async def evaluate_node(session_id: str, node_id: str, request: EvalRequest):
    """
    Evaluates a user's quiz answer and reasoning.
    """
    tree = session_service.get_session(session_id)
    node = session_service.get_node(tree, node_id)
    
    if node.state != NodeState.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Node must be ACTIVE to evaluate. Current state: {node.state}")
        
    is_correct = (request.selected_option_id == request.correct_option_id)
    
    # AI Evaluation of reasoning
    eval_data = await ai_service.evaluate_reasoning(
        node_label=request.node_label,
        question=request.question,
        correct_answer=request.correct_option_id, # Or use text, but ID is fine for context
        user_reasoning=request.reasoning
    )
    
    reasoning_score = eval_data.get("reasoning_score", 1)
    reasoning_feedback = eval_data.get("reasoning_feedback", "No feedback provided.")
    
    nodes_unlocked = []
    bridge_node = None
    message = ""
    
    if is_correct:
        node.fail_count = 0
        nodes_unlocked = graph_service.unlock_after_mastery(tree, node_id)
        message = "Correct! Well done."
    else:
        node.fail_count += 1
        message = "Incorrect answer."
        if node.fail_count >= 3 and not any(n.parent_node_id == node_id for n in tree.nodes):
            bridge_node = graph_service.create_bridge_node(tree, node_id)
            message += " You've failed 3 times. A bridge node has been created to help you."
            
    session_service.update_session(session_id, tree)
    
    return EvalResult(
        correct=is_correct,
        reasoning_score=reasoning_score,
        reasoning_feedback=reasoning_feedback,
        nodes_unlocked=nodes_unlocked,
        bridge_node_created=bridge_node,
        message=message
    )
