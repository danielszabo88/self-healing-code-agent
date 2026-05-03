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


def clean_output(text: str):
    text = text.replace("```", "")
    text = text.strip()
    return text[:500]

def validate_input(code: str):
    if not code.strip():
        return False, "Empty input"

    if len(code) > 2000:
        return False, "Input too long"

    return True, ""

def validate_output(text: str):
    if len(text) < 5:
        return False, "Output too short"

    if len(text) > 500:
        return False, "Output too long"

    return True, ""

def build_prompt(code: str):
    return f"""
Explain what this code does in simple terms.

Rules:
- 1–2 sentences only
- No markdown
- No code blocks
- No extra commentary

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
    valid, error = validate_input(req.code)
    if not valid:
        return {"explanation": f"Input error: {error}"}

    prompt = build_prompt(req.code)
    raw = ask_llm(prompt)
    clean = clean_output(raw)

    valid_out, out_error = validate_output(clean)
    if not valid_out:
        return {"explanation": f"Output error: {out_error}"}

    return {
        "explanation": clean
    }