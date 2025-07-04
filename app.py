import streamlit as st
import ollama
import re
import json
import requests

st.set_page_config(page_title="Code Reviewer", layout="wide")

st.title("🧠 Code Reviewer")

API_URL = "http://localhost:8000/generate-reviews"

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
        response = requests.post(API_URL, json={"code": input_code})
        # suggestions = response.json()["suggestion"]  # ✅ no need for json.loads()
       
        try:
            response_json = response.json()
            # suggestions = json.loads(response_json["message"]["content"])
            suggestions = response.json()["suggestion"]  # ✅ no need for json.loads()
            st.session_state["original_code"] = input_code
            st.session_state["current_code"] = input_code
            st.session_state["suggestions"] = suggestions
            st.success(f"✅ {len(suggestions)} suggestion(s) generated.")
        except Exception as e:
            st.error("❌ Could not parse suggestions from DeepSeek.")
            st.code(response.text)  # or response.json() if it's valid JSON
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
                    #  Unescape the replacement string
                    replacement = replacement.encode().decode('unicode_escape')
                    modified_code = re.sub(pattern, replacement, modified_code, count=1)
                except Exception as e:
                    st.error(f"Failed to apply suggestion: {e}")

        st.markdown("#### ✨ Updated Code")
        st.code(modified_code, language="html")

        # Update stored code
        st.session_state["current_code"] = modified_code
