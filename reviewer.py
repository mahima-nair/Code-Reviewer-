import requests
from typing import Optional
import ollama
import re
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

def load_prompt_template():
    with open("reviewprompt.txt", "r") as f:
        return f.read()
    
def build_prompt(code_text):
    prompt_template = load_prompt_template()
    return f"{prompt_template}\n\n{code_text}"

class CodeReviewer:
    def __init__(self, model_name: str = "deepseek-coder-v2:latest", base_url: str = "http://localhost:11434"):
        
        self.model_name = model_name
        self.base_url = base_url

    def generate_review(self, code: str) -> str:

        prompt = build_prompt (code)
       
        response = ollama.chat(
            model="deepseek-coder-v2",
            messages=[{"role": "user", "content": prompt}]
        )

        # if response.status_code != 200:
        #     raise Exception(f"Error from Ollama API: {response.text}")
        #print("🔁 Raw ollama response:", response)  
       
        #print("🧪 LLM raw output:\n", response.message["content"])
        filename = f"reviewed_code.txt"
        with open(filename, "w") as f:
            f.write(response.message["content"])
            print(f"✅ Reviewed code saved to {filename}")


        result = response.json()
        return response.message["content"]
        # return {"message": {"content": result}}

       