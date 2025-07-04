from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from reviewer import CodeReviewer
import json

app = FastAPI(title = "CodeReviewer API", version = "1.0")


reviewer = CodeReviewer()  # Uses CodeCommentor model that contains the prompt

class CodeRequest(BaseModel):
    code: str
   

class CodeResponse(BaseModel):
    # suggestion: str
    suggestion: List[Dict[str, str]]

@app.get("/")
def index():
    return {"Welome to Code Reviewer!"}

@app.post("/generate-reviews", response_model=CodeResponse)

def generate_reviews(request: CodeRequest):
    try:
        #code = json.dumps({"code": request.code})
        result = reviewer.generate_review(request.code)
        # return {"Suggestions": result}
        # return {"message": {"content": result}} 
        raw_json_string = reviewer.generate_review(request.code)
        suggestions  = json.loads(raw_json_string)  
        return {"suggestion": suggestions } 
    except Exception as e:
        # print("❌ Backend error:", e)  
        raise HTTPException(status_code=500, detail=str(e))
