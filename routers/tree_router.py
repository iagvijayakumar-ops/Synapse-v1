import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from services import ai_service, graph_service, session_service, pdf_service
from models.skill_tree import SkillTree

router = APIRouter(prefix="/tree", tags=["Tree Generation"])

class TreeRequest(BaseModel):
    topic: str

@router.post("/generate", response_model=SkillTree)
async def generate_tree(request: TreeRequest):
    """
    Generates a new skill tree from a text topic.
    """
    session_id = str(uuid.uuid4())
    raw_json = await ai_service.generate_skill_tree_json(request.topic)
    
    try:
        tree = graph_service.build_graph(raw_json, request.topic, session_id)
        session_service.create_session(tree)
        return tree
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-pdf", response_model=SkillTree)
async def generate_tree_from_pdf(file: UploadFile = File(...)):
    """
    Extracts text from PDF and generates a skill tree.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    content = await file.read()
    extracted_text = pdf_service.extract_text_from_pdf(content)
    
    # Truncate for prompt efficiency
    topic_input = extracted_text[:3000]
    
    session_id = str(uuid.uuid4())
    raw_json = await ai_service.generate_skill_tree_json(topic_input)
    
    try:
        tree = graph_service.build_graph(raw_json, "Extracted from PDF", session_id)
        session_service.create_session(tree)
        return tree
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=SkillTree)
async def get_tree(session_id: str):
    """
    Retrieves the current state of a skill tree.
    """
    return session_service.get_session(session_id)

@router.delete("/{session_id}")
async def delete_tree(session_id: str):
    """
    Deletes a session.
    """
    session_service.delete_session(session_id)
    return {"message": "Session deleted"}
