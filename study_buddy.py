import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env (if present)
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.3-70b-versatile"


def call_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # Fallback for offline or API failures — return a helpful placeholder
        placeholder = (
            "[LLM unavailable — running in offline mode].\n\n"
            "Summary: Unable to contact LLM. Please check GROQ_API_KEY and network.\n"
            "Key Points:\n1) Unable to generate explanation due to connection error.\n"
        )
        return placeholder


def explainer_agent(text: str, level: str = "Detailed") -> dict:
    system_prompt = (
        "You are an explainer agent. "
        "Explain concepts in simple English for a beginner student. "
        "Output JSON-like text containing a short explanation and key points."
    )

    user_prompt = f"""
Read the following study text and produce a concise explanation at the requested level ({level}).
1) A short explanation (3-5 sentences).
2) 3-5 key points (numbered list).

Text:
{text}
"""

    raw = call_llm(system_prompt, user_prompt)
    return {"explanation_text": raw}


def quiz_agent(explanation: str, difficulty: str = "Medium", num_questions: int = 5) -> str:
    system_prompt = (
        "You are a quiz generator agent. "
        "Create straightforward multiple-choice questions appropriate for the requested difficulty."
    )

    user_prompt = f"""
Using the explanation and key points below, create {num_questions} quiz questions at '{difficulty}' difficulty.
For each question, provide:
- Question
- 4 options (A, B, C, D)
- Correct answer letter

Explanation and key points:
{explanation}
"""

    quiz_text = call_llm(system_prompt, user_prompt)
    return quiz_text


if __name__ == "__main__":
    # Lightweight CLI fallback
    print("This module provides `explainer_agent` and `quiz_agent` for the Streamlit app.")
