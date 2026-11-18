# 📄 Resume Analyzer

> Assignment 3 – Gen AI · Problem Statement 41
> By **Sai Ukarande**

Students often don't know why their resumes get rejected. **Resume Analyzer** compares a resume with a job description and tells you how well they match, which skills you already have, which ones are missing, and 3 concrete tips to improve.

It runs **fully offline** using a local LLM through [Ollama](https://ollama.com), so there is no API key, no cost, and your resume never leaves your computer.

---

## ✨ Features

- Upload a resume as a **PDF** (text extracted with PyPDF2)
- Paste any **job description**
- Get a **match score (0–100)** shown with a progress bar and a Strong / Moderate / Weak verdict
- See **matched skills** and **missing skills** side by side
- Receive **3 specific tips** to improve the resume for that job
- Handles bad model output: JSON mode, temperature 0, regex JSON extraction and one automatic retry
- Clear error messages for scanned PDFs and when Ollama isn't running

## 🧰 Tech Stack

| Part | Tool |
|---|---|
| Language | Python 3.11 |
| UI | Streamlit |
| PDF reading | PyPDF2 |
| LLM | `qwen2.5:3b` via Ollama (any Ollama chat model works) |
| HTTP | requests |

## 🔄 How It Works

```
Resume PDF ──► PyPDF2 ──► resume text ─┐
                                       ├─► prompt ─► Ollama (local LLM) ─► JSON ─► Streamlit UI
Job description (pasted) ──────────────┘
```

The model is asked to return only this JSON, which the app validates and displays:

```json
{
  "match_score": 72,
  "matched_skills": ["Python", "SQL"],
  "missing_skills": ["Docker", "AWS"],
  "tips": ["...", "...", "..."]
}
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/download) installed and running

### 2. Pull a model
```bash
ollama pull qwen2.5:3b
ollama list        # check the exact model name
```

### 3. Install and run
```bash
git clone https://github.com/YOUR_USERNAME/resume-analyzer.git
cd resume-analyzer
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at http://localhost:8501.

> **Windows tip:** if `streamlit` isn't recognized, use `python -m streamlit run app.py` as shown above.

### 4. Use it
1. Enter your model name in the sidebar (default: `qwen2.5:3b`)
2. Upload your resume PDF
3. Paste the job description
4. Click **Analyze**

## 📸 Screenshots

| Score and skills | Tips |
|---|---|
| ![Result 1](screenshots/result1.png) | ![Result 2](screenshots/result2.png) |

## 📁 Project Structure

```
resume-analyzer/
├── app.py              # Streamlit app: PDF reading, prompt, LLM call, UI
├── requirements.txt    # Python dependencies
├── screenshots/        # Output screenshots
└── README.md
```

## ⚠️ Limitations

- Scanned (image-only) PDFs can't be read, because there is no OCR yet
- A small 3B model gives an **estimated** score, not a real ATS result, so treat it as guidance
- Very long resumes or job descriptions are truncated to 6000 characters each

## 🔮 Future Improvements

- OCR support for scanned resumes
- Compare against a fixed skill list for more consistent scores
- Export the analysis as a PDF report

## 🙌 Acknowledgements

Built with [Streamlit](https://streamlit.io), [Ollama](https://ollama.com), and [PyPDF2](https://pypdf2.readthedocs.io).
