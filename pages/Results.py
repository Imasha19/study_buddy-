import re
import streamlit as st
from datetime import datetime


def format_quiz_as_points(quiz_text: str) -> str:
    if not quiz_text:
        return ""
    out_lines = []
    for line in quiz_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r'^(?:\d+[\.)]|Question[:\s]|Q[:\s])', s, re.I):
            cleaned = re.sub(r'^(?:\d+[\.)]\s*|Question[:\s]*|Q[:\s]*)', '', s, flags=re.I)
            out_lines.append(f"- {cleaned}")
        elif re.match(r'^[A-D][\.|\)]', s, re.I):
            out_lines.append(f"    - {s}")
        else:
            out_lines.append(f"- {s}")
    return "\n".join(out_lines)


st.title("📚 Results — AI Study Buddy")

last_exp = st.session_state.get('last_explanation', '')
last_quiz = st.session_state.get('last_quiz', '')

if not last_exp and not last_quiz:
    st.info("No results available. Run a study session in the main app first.")
else:
    st.markdown("#### 🎯 Simplified Explanation")
    st.markdown(last_exp or "_(No explanation available)_")

    st.divider()
    st.markdown(f"#### 🧠 Quiz ({st.session_state.get('difficulty','N/A')} Level)")
    formatted = format_quiz_as_points(last_quiz)
    if formatted:
        st.markdown(formatted)
    else:
        st.info("No quiz generated yet.")

    st.divider()
    export = f"SIMPLIFIED EXPLANATION:\n{last_exp}\n\nQUIZ:\n{formatted}\n"
    st.download_button("📥 Export Results", data=export, file_name=f"study_results_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
