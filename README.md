# SYNAPSE Backend 🧠⚡

Welcome to the **SYNAPSE** backend—an AI-powered adaptive learning engine. This backend uses high-speed LLM inference (via Groq) to generate dynamic learning paths (DAGs), micro-lessons, and interactive evaluations.

## 🚀 Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **AI Engine**: Groq SDK (Llama-3.3-70B)
- **PDF Processing**: `pdfplumber`
- **Logic**: Custom Directed Acyclic Graph (DAG) state management
- **Storage**: Thread-safe in-memory session management

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.11+
- A valid Groq API Key

### 2. Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```
The API will be live at `http://localhost:8000`. 
View the interactive Swagger docs at `http://localhost:8000/docs`.

---

## 📡 API Documentation for Frontend

### 1. Tree Generation
Start here to create a learning journey.

#### **POST** `/tree/generate`
Generates a skill tree from a text topic.
- **Body**: `{ "topic": "Quantum Computing" }`
- **Returns**: A full `SkillTree` object including a `session_id`. **Store this session_id!**

#### **POST** `/tree/generate-from-pdf`
Generates a skill tree from a PDF syllabus.
- **Body**: `multipart/form-data` with a `file` field (.pdf).
- **Returns**: `SkillTree` object with `session_id`.

---

### 2. Node Operations
Interact with specific concepts in the tree.

#### **GET** `/node/{session_id}/{node_id}/lesson`
Fetches a 150-word micro-lesson and a 4-option MCQ quiz.
- **Rules**: Node must be `ACTIVE`.
- **Response**: 
```json
{
  "node_id": "node_1",
  "title": "Introduction to Qubits",
  "content": "...",
  "quiz": {
    "question": "...",
    "options": [{"id": "A", "text": "..."}, ...],
    "correct_option_id": "B",
    "explanation": "..."
  }
}
```

#### **POST** `/node/{session_id}/{node_id}/evaluate`
Submits a quiz answer and the user's reasoning.
- **Body**:
```json
{
  "session_id": "...",
  "node_id": "...",
  "selected_option_id": "A",
  "correct_option_id": "B",
  "question": "The quiz question text",
  "node_label": "Node Title",
  "reasoning": "User's explanation (min 10 chars)"
}
```
- **Logic**:
  - **On Success**: Unlocks next dependent nodes.
  - **On 3 Fails**: Automatically spawns a "Bridge Node" (Foundation lesson) and links it as a prerequisite.

---

### 3. Progress Tracking

#### **GET** `/session/{session_id}/progress`
Returns overall statistics for the user's journey.
- **Response**:
```json
{
  "topic": "Quantum Computing",
  "total_nodes": 12,
  "mastered": 3,
  "active": 2,
  "locked": 7,
  "completion_percentage": 25.0,
  "mastered_node_ids": [...],
  "active_node_ids": [...]
}
```

---

## 💡 Integration Tips for Frontend

1. **Session Persistence**: Since the backend uses in-memory storage, sessions will be lost if the server restarts. Ensure your frontend handles a "Session Not Found (404)" error by redirecting the user to the "Generate" page.
2. **State Management**: The `SkillTree` object contains `nodes` and `edges`. Use these to render a graph (e.g., using `react-flow` or `d3.js`).
3. **Node Colors**:
   - `LOCKED`: Grey/Disabled.
   - `ACTIVE`: Vibrant/Clickable.
   - `MASTERED`: Green/Completed.
4. **Reasoning Field**: Encourage users to write meaningful reasoning! The AI evaluates this to give a `reasoning_score` (1-5), which can be used to show users how deep their understanding is.
5. **CORS**: Enabled for all origins (`*`), so you won't have issues during local development.

---

## 🏗️ Project Structure
```text
synapse-backend/
├── main.py          # App entry & Routing
├── models/          # Pydantic schemas (Data Contracts)
├── services/        # AI logic, Graph logic, PDF logic
└── routers/         # API Endpoint definitions
```
