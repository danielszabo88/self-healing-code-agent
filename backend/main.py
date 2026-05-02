from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    task: str

def build_prompt(task: str):
    return f"""
Return ONLY valid JSON:

{{
  "code": "python code here",
  "explanation": "short explanation"
}}

Task:
{task}
"""

def ask_llm(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        }
    )
    raw = response.json().get("response", "")
    print("RAW LLM OUTPUT:", raw) 

    return raw

def parse_output(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "code": "",
            "explanation": "Failed to parse model output"
        }

@app.post("/run")
async def run(req: RequestData):
    prompt = build_prompt(req.task)
    raw = ask_llm(prompt)
    parsed = parse_output(raw)

    return parsed