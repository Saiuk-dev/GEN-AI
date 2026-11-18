# Resume Analyzer (PS 41)
Upload a resume PDF, paste a job description, get a match score, matched/missing skills and 3 tips.
Uses PyPDF2 for PDF text, Streamlit for the UI, and a local LLM via Ollama (no API key needed).

## Run
1. Install Ollama and pull a model: `ollama pull llama3.2:3b` (check names with `ollama list`)
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
4. Enter your model name in the sidebar if it differs from the default.
