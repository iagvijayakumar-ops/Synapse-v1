import json
import os
from groq import Groq
from config import GROQ_API_KEY
from fastapi import HTTPException

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)
# Using a powerful stable model from Groq
DEFAULT_MODEL = "llama-3.3-70b-versatile"

def clean_json_response(text: str) -> dict:
    """
    Strips markdown fences and attempts to parse JSON safely.
    """
    text = text.strip()
    
    # Remove markdown code block markers if present
    if "```" in text:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        else:
            text = text.split("```")[1].split("```")[0]
    
    text = text.strip()
    
    # Find outermost braces
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
        
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}\nRaw text: {text}")
        raise ValueError("AI returned invalid JSON format")

async def call_groq(prompt: str, response_format: str = "json_object") -> str:
    """
    Helper to call Groq API with specific formatting requirements.
    """
    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only returns data in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": response_format} if response_format == "json_object" else None,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API Error: {str(e)}")

async def generate_skill_tree_json(topic: str) -> dict:
    """
    Generates a DAG of concepts for a given topic using Groq.
    """
    prompt = f"""
    Generate a Directed Acyclic Graph (DAG) of learning concepts for the topic: "{topic}".
    Return ONLY a valid JSON object with this schema:
    {{
      "nodes": [
        {{"id": "node_1", "label": "Concept Name", "description": "One sentence description", "prerequisites": []}}
      ],
      "edges": [
        {{"source": "node_1", "target": "node_2"}}
      ]
    }}
    Rules:
    - 8 to 15 nodes total.
    - No circular dependencies.
    - Exactly one root node (no prerequisites).
    - Every non-root node must have at least one prerequisite.
    - Prerequisites must be a list of node IDs that must be mastered first.
    - Source in edges must be mastered before target.
    - Return ONLY the JSON object.
    """
    
    try:
        response_text = await call_groq(prompt)
        return clean_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")

async def generate_micro_lesson(node_label: str, node_description: str, topic: str) -> dict:
    """
    Generates a micro-lesson and a quiz for a node using Groq.
    """
    prompt = f"""
    Create a micro-lesson for the concept "{node_label}" within the context of "{topic}".
    Concept Description: {node_description}

    Return ONLY a valid JSON object with this schema:
    {{
      "title": "...",
      "content": "...", 
      "quiz": {{
        "question": "...",
        "options": [
          {{"id": "A", "text": "..."}},
          {{"id": "B", "text": "..."}},
          {{"id": "C", "text": "..."}},
          {{"id": "D", "text": "..."}}
        ],
        "correct_option_id": "A",
        "explanation": "..."
      }}
    }}
    Rules:
    - Content must be approximately 150 words.
    - Use real-world examples in the explanation.
    - Quiz must have exactly 4 options.
    - correct_option_id must be one of A, B, C, D.
    """
    
    try:
        response_text = await call_groq(prompt)
        return clean_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Lesson Generation Error: {str(e)}")

async def evaluate_reasoning(node_label: str, question: str, correct_answer: str, user_reasoning: str) -> dict:
    """
    Evaluates the depth of user reasoning for a quiz answer using Groq.
    """
    prompt = f"""
    Evaluate the following reasoning for a quiz question on "{node_label}".
    Question: {question}
    Correct Answer: {correct_answer}
    User's Reasoning: {user_reasoning}

    Return ONLY a valid JSON object with this schema:
    {{
      "reasoning_score": 4, 
      "reasoning_feedback": "..."
    }}
    Rules:
    - reasoning_score: 1-5 integer (1=wrong/shallow, 5=deep understanding).
    - reasoning_feedback: 1-2 sentences of constructive feedback.
    """
    
    try:
        response_text = await call_groq(prompt)
        return clean_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Evaluation Error: {str(e)}")
