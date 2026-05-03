from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import subprocess
import tempfile
import re
import json
import os

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

def run_code(code: str):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(
            ["python", path],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout or result.stderr
    
    except subprocess.TimeoutExpired:
        return "TimeoutError: execution took too long"

    except Exception as e:
        return f"RuntimeError: {str(e)}"
    
    finally:
        os.remove(path)
    
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
    
def safe_parse_llm(text):
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
    except:
        pass

    return {
        "explanation": "Could not parse model output",
        "error": "parse_failed"
    }

def validate_input(code: str):
    if not code.strip():
        return False, "Empty input"
    if len(code) > 2000:
        return False, "Too long"
    return True, ""

def validate_code_execution(code: str):
    blocked = ["os.system", "subprocess", "open(", "eval(", "exec("]
    for b in blocked:
        if b in code:
            return False, f"Blocked: {b}"
    return True, ""

def build_prompt(code: str):
    return f"""
Return ONLY valid JSON in this format:

{{
  "explanation": "1 short sentence explaining what the code does",
  "error": "none if no error, otherwise the runtime error"
}}

RULES:
- No markdown
- No extra text
- No guessing

Code:
{code}
"""

def has_error(output: str):
    out = output.lower()
    return (
        "traceback" in out or
        "zerodivisionerror" in out or
        "syntaxerror" in out or
        "exception" in out
    )

def simple_fix(code: str, output: str):
    out = output.lower()

    if "zerodivisionerror" in out:
        return re.sub(r"/\s*0", "/ 1", code)

    if "syntaxerror" in out:
        return code.strip() + "\n"

    return None

def run_agent(code: str):
    original_code = code
    current_code = code

    for _ in range(3):
        output = run_code(current_code)

        if not has_error(output):
            return original_code, current_code, output

        fixed = simple_fix(current_code, output)

        if not fixed:
            return original_code, current_code, output

        current_code = fixed

    return original_code, current_code, "Failed after 3 attempts"

@app.post("/run")
async def run(req: RequestData):
    # 1. Input validation
    valid, error = validate_input(req.code)
    if not valid:
        return {"error": error}

    # 2. Security check
    safe, error = validate_code_execution(req.code)
    if not safe:
        return {"error": error}

    # 3. Run agent (fix + execute)
    original_code, final_code, output = run_agent(req.code)

    # 4. Explain FINAL code (not original)
    prompt = build_prompt(final_code)
    raw = ask_llm(prompt)
    parsed = safe_parse_llm(raw)
    explanation = parsed.get("explanation", "No explanation")
    llm_error = parsed.get("error", "none")
    
    if llm_error == "parse_failed":
        return {
            "original_code": original_code,
            "final_code": final_code,
            "explanation": "LLM output invalid format",
            "output": output,
            "llm_error": llm_error
        }
        
    return {
        "original_code": original_code,
        "final_code": final_code,
        "explanation": explanation,
        "output": output,
        "llm_error": llm_error
    }