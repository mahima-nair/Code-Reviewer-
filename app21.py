import streamlit as st
import ollama
import re
import json

st.set_page_config(page_title="Code Reviewer", layout="wide")

st.title(" Code Reviewer")

# --- 1. User Input
st.subheader("Input Code")
default_code = """<div class="login-box">
  <h2>Login</h2>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>Email</label>
      <input type="text" v-model="text" required />
    </div>
    <div class="form-group">
      <label>Password</label>
      <input type="text" v-model="text" required />
    </div>
    <button type="submit">Submit</button>
  </form>
</div>"""
input_code = st.text_area("Paste your code here", default_code, height=300)

if st.button("🔍 Review Code"):
    with st.spinner("Generating Suggestions"):
        # --- 2. Prompt for LLM
        prompt = f"""
You are a senior code reviewer that analyzes source code line and detects violations of programming best practices. Your job is to review the following code thoroughly for:

- Best practices  
- Security issues  
- Maintainability  
- Readability  
- Code smells  
- Missing validations or checks  
- Incorrect or unsafe HTML attributes (e.g., input types)

DO NOT change, rewrite, or modify the code.

Only provide suggestion when there's something genuinely worth noting or improving.  


Your task is to return a JSON list where each element is a suggestion in the following format:
[
{{
  "description": "Brief explanation of why the line or block is a violation of best practices and suggestion on how it can be improved.",
  "pattern": "The original line(s) of code that should be improved.",
  "replacement": "The suggested corrected version of that line(s)."
}}
]

Requirements:
- Only return the JSON list (no additional explanations or text).
- The "description" should be concise, actionable, and easy to understand.  
- The "pattern" and "replacement" values should be **exact code snippets** (not paraphrased descriptions).
- The "replacement" should aim to follow modern, clean, readable, and idiomatic coding practices.
- Only include code that has issues — do not return entries for lines that follow best practices.
- Do not use comments in the replacement.
- Be conservative: only suggest replacements when they clearly improve the code according to best practices.
- Include multi-line "pattern" and "replacement" fields if the issue spans multiple lines.
- Provide each and every suggestion separately. Do not combine or club the suggestions together.

Only return a clean JSON array. No extra text.

### Code to review:
{input_code}
"""
#         prompt = """
# You are an automated code review assistant that analyzes source code line by line and detects violations of programming best practices.

# Your task is to return a JSON list where each element is a suggestion in the following format:

# {
#   "suggestion": "Brief explanation of why the line or block is a violation of best practices.",
#   "pattern": "The original line(s) of code that should be improved.",
#   "replacement": "The suggested corrected version of that line(s)."
# }

# Requirements:
# - Only return the JSON list (no additional explanations or text).
# - The "pattern" and "replacement" values should be **exact code snippets** (not paraphrased descriptions).
# - The "replacement" should aim to follow modern, clean, readable, and idiomatic coding practices.
# - Do NOT repeat suggestions for the same issue multiple times unless they apply to different locations.
# - Only include code that has issues — do not return entries for lines that follow best practices.
# - Do not use comments in the replacement unless absolutely necessary.
# - Be conservative: only suggest replacements when they clearly improve the code according to best practices.
# - Include multi-line "pattern" and "replacement" fields if the issue spans multiple lines.

# ### Example Output:
# [
#   {{
#     "description": "Use a more descriptive class name for the login box.",
#     "pattern": "class=\\\"login-box\\\"",
#     "replacement": "class=\\\"login-form-container\\\""
#   }}
#   ]
# Code to review:
# {input_code}
# """

        # --- 3. Call DeepSeek via Ollama
        response = ollama.chat(
            model="deepseek-coder-v2",
            messages=[{"role": "user", "content": prompt}]
        )
        with open('response.txt', 'w') as f:
            f.write(response["message"]["content"])

        try:
            # Use regex to extract the first JSON array (everything between square brackets)
            raw_text = response['message']['content']
            match = re.search(r'\[\s*{.*?}\s*\]', raw_text, re.DOTALL)

            if match:
              json_str = match.group(0)
              suggestions = json.loads(json_str)  # ✅ Correct usage
            else:
              suggestions = []

            #suggestions = json.loads(json_str["message"]["content"])
            st.session_state["original_code"] = input_code
            st.session_state["current_code"] = input_code
            st.session_state["suggestions"] = suggestions
            st.success(f"✅ {len(suggestions)} suggestion(s) generated.")
        except Exception as e:
            st.error("❌ Could not parse suggestions from DeepSeek.")
            st.code(response["message"]["content"])
            suggestions = []

# --- 4. Suggestion Display and Real-Time Patch
if "suggestions" in st.session_state and st.session_state["suggestions"]:
    st.subheader("✅ Suggested Improvements")

    modified_code = st.session_state["original_code"]
        # Save response to response.txt

    # Layout
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("#### Original Code")
        st.code(st.session_state["original_code"], language="html")

    with col2:
        for idx, suggestion in enumerate(st.session_state["suggestions"]):
            key = f"suggestion_{idx}"
            if st.checkbox(suggestion["description"], key=key):
                try:
                    pattern = suggestion["pattern"]
                    replacement = suggestion["replacement"]
                    if isinstance(replacement, list):
                      replacement = "\n".join(replacement)  # ✅ Convert list to string
            #modified_code = re.sub(pattern, replacement, modified_code, count=1)
                    modified_code = re.sub(re.escape(pattern), replacement, modified_code, count=1)
                except Exception as e:
                    st.error(f"Failed to apply suggestion: {e}")

        st.markdown("#### ✨ Updated Code")
        st.code(modified_code, language="html")

        # Update stored code
        st.session_state["current_code"] = modified_code
