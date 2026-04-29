"""
SYNAPSE API - AI-Powered Adaptive Learning Platform

ENDPOINTS:

1. Tree Generation
   - POST /tree/generate
     Body: {"topic": "Machine Learning"}
   - POST /tree/generate-from-pdf
     Body: Multipart form-data with "file" (.pdf)
   - GET /tree/{session_id}
   - DELETE /tree/{session_id}

2. Node Operations
   - GET /node/{session_id}/{node_id}/lesson
   - POST /node/{session_id}/{node_id}/evaluate
     Body: {
       "session_id": "...",
       "node_id": "...",
       "selected_option_id": "A",
       "correct_option_id": "B",
       "question": "...",
       "node_label": "...",
       "reasoning": "My reasoning for this answer is..."
     }

3. Session Progress
   - GET /session/{session_id}/progress

"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tree_router, node_router, session_router

app = FastAPI(
    title="Synapse API",
    description="Adaptive Learning Platform Backend",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tree_router.router)
app.include_router(node_router.router)
app.include_router(session_router.router)

@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "service": "Synapse API"}

@app.on_event("startup")
async def startup_event():
    print("Synapse API started")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
