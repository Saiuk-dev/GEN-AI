"""PS 41 - Resume Analyzer
Upload a resume PDF + paste a job description -> match score, matched skills,
missing skills and 3 tips, using a local LLM served by Ollama.
"""
import json
import re

import requests
import streamlit as st
from PyPDF2 import PdfReader

OLLAMA_URL = "http://localhost:11434/api/chat"
MAX_CHARS = 6000  # keep prompts small so a 3B-class local model can handle them

PROMPT = """You are an experienced technical recruiter and ATS (applicant tracking system) expert.
Compare the RESUME with the JOB DESCRIPTION below.

Rules:
- Base everything ONLY on the text given. Do not invent skills the resume does not mention.
- "matched_skills": skills/tools/qualifications required by the job that appear in the resume.
- "missing_skills": skills/tools/qualifications required by the job that are NOT in the resume.
- "match_score": integer 0-100 based on how much of the job's requirements the resume covers.
- "tips": exactly 3 short, specific suggestions to improve this resume for this job.

Return ONLY valid JSON in exactly this format, with no extra text:
{"match_score": 0, "matched_skills": ["..."], "missing_skills": ["..."], "tips": ["...", "...", "..."]}

RESUME:
<<RESUME>>

JOB DESCRIPTION:
<<JD>>
"""


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages).strip()


def call_ollama(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 8192},
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"]


def parse_json(raw: str) -> dict:
    # Some models (e.g. Qwen3) emit <think>...</think>; strip it first.
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")
    data = json.loads(match.group(0))

    score = int(float(data.get("match_score", 0)))
    return {
        "match_score": max(0, min(100, score)),
        "matched_skills": [str(s) for s in data.get("matched_skills", [])],
        "missing_skills": [str(s) for s in data.get("missing_skills", [])],
        "tips": [str(t) for t in data.get("tips", [])][:3],
    }


def analyze(model: str, resume: str, jd: str) -> dict:
    prompt = PROMPT.replace("<<RESUME>>", resume[:MAX_CHARS]).replace("<<JD>>", jd[:MAX_CHARS])
    last_err = None
    for _ in range(2):  # one retry if the model returns bad JSON
        try:
            return parse_json(call_ollama(model, prompt))
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
    raise ValueError(f"Model did not return valid JSON: {last_err}")


# ---------------- UI ----------------
st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 Resume Analyzer")
st.caption("Find out how well your resume matches a job description, and what's missing.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Ollama model name", value="llama3.2:3b",
                          help="Run `ollama list` in a terminal and paste the exact name.")
    st.info("Make sure Ollama is running (`ollama serve`).")

col1, col2 = st.columns(2)
with col1:
    pdf = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    jd = st.text_area("Paste the job description", height=250)

if st.button("Analyze", type="primary"):
    if not pdf or not jd.strip():
        st.warning("Please upload a resume PDF and paste a job description.")
        st.stop()

    resume_text = extract_pdf_text(pdf)
    if len(resume_text) < 50:
        st.error("Couldn't read text from this PDF (it may be a scanned image). Try a text-based PDF.")
        st.stop()

    try:
        with st.spinner("Analyzing with the local model..."):
            result = analyze(model, resume_text, jd)
    except requests.exceptions.ConnectionError:
        st.error("Can't reach Ollama. Start it with `ollama serve` and try again.")
        st.stop()
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

    score = result["match_score"]
    st.subheader(f"Match score: {score}%")
    st.progress(score / 100)
    if score >= 75:
        st.success("Strong match.")
    elif score >= 50:
        st.warning("Moderate match - some gaps to close.")
    else:
        st.error("Weak match - the resume is likely to be filtered out.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ✅ Matched skills")
        for s in result["matched_skills"] or ["None found"]:
            st.write(f"- {s}")
    with c2:
        st.markdown("### ❌ Missing skills")
        for s in result["missing_skills"] or ["None - great!"]:
            st.write(f"- {s}")

    st.markdown("### 💡 Tips to improve")
    for i, t in enumerate(result["tips"], 1):
        st.write(f"{i}. {t}")
