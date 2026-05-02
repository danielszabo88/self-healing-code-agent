from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    code: str

def build_prompt(code: str):
    return f"""
Explain what this code does in simple terms.
Explain code in 1–2 sentences.
No extra commentary.
No advice.

Code:
{code}
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
    return response.json().get("response", "")

@app.post("/run")
async def run(req: RequestData):
    prompt = build_prompt(req.code)
    result = ask_llm(prompt)

    return {
        "explanation": result
    }