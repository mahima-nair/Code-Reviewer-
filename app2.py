import streamlit as st
import ollama
import re
import json

st.set_page_config(page_title="Code Reviewer", layout="wide")

st.title("🧠 Code Reviewer")

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
    with st.spinner("Generating Comments and Suggestions"):
        # --- 2. Prompt for LLM
        prompt = f"""
You are a senior code reviewer. Your job is to review the following code thoroughly for:

- Best practices  
- Security issues  
- Maintainability  
- Readability  
- Code smells  
- Missing validations or checks  
- Incorrect or unsafe HTML attributes (e.g., input types)

DO NOT change, rewrite, or modify the code.
Keep it concise, actionable, and easy to understand.  
Only provide suggestion when there's something genuinely worth noting or improving.  
Provide each and every suggestion separately. Do not combine or club the suggestions together.

### Format for Output:
[
  {{
    "description": "...",
    "pattern": "...",
    "replacement": "..."
  }}
]

### Example Output:
[
  {{
    "description": "Use a more descriptive class name for the login box.",
    "pattern": "class=\\\"login-box\\\"",
    "replacement": "class=\\\"login-form-container\\\""
  }},
  {{
    "description": "Use input type='email' for email field.",
    "pattern": "<input type=\\\"text\\\" v-model=\\\"text\\\" required />",
    "replacement": "<input type=\\\"email\\\" v-model=\\\"email\\\" required />",
    "condition": "email"
  }},

  {{
    "description": "Use input type='password' for password field.",
    "pattern": "<input type=\\\"text\\\" v-model=\\\"text\\\" required />",
    "replacement": "<input type=\\\"email\\\" v-model=\\\"email\\\" required />",
    "condition": "email"
  }}


]

Only return a clean JSON array. No extra text.

### Code to Review:
{input_code}
"""

        # --- 3. Call DeepSeek via Ollama
        response = ollama.chat(
            model="deepseek-coder-v2",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            suggestions = json.loads(response["message"]["content"])
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
                    modified_code = re.sub(pattern, replacement, modified_code, count=1)
                except Exception as e:
                    st.error(f"Failed to apply suggestion: {e}")

        st.markdown("#### ✨ Updated Code")
        st.code(modified_code, language="html")

        # Update stored code
        st.session_state["current_code"] = modified_code
