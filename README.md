# Resume Screening Agent

A Python application for screening PDF resumes against a job description and producing ranked candidate reports.

## Project structure

```text
resume-screening-agent/
├── app.py                  # Streamlit UI (to be implemented)
├── main.py                 # CLI entry point (to be implemented)
├── config.py               # Shared configuration (to be implemented)
├── requirements.txt
├── resumes/                # Input PDF resumes
├── jd/                     # Input job descriptions
├── output/                 # Generated rankings and reports
└── src/
    ├── parser.py           # PDF parsing
    ├── extractor.py        # Candidate data extraction
    ├── embedder.py         # Text embeddings
    ├── scorer.py           # Candidate scoring
    ├── ranker.py           # Candidate ranking
    ├── report.py           # Report generation
    └── utils.py            # Shared helpers
```

## Setup

Use Python 3.10 or later, then install the dependencies:

```bash
pip install -r requirements.txt
```

## PDF parsing

`src/parser.py` reads each `.pdf` file in a resume folder and returns normalized
text keyed by the original file name. Non-PDF files are ignored.

```python
from src.parser import read_resumes

resume_texts = read_resumes("resumes")
# {"john.pdf": "...", "alice.pdf": "..."}
```

Run the parser tests with:

```bash
python -m unittest discover -s tests -v
```

## Candidate extraction

`src/extractor.py` converts resume text into a consistent Python dictionary. It
uses regex and text-pattern heuristics to identify contact details, skills,
education, stated years of experience, and listed projects.

```python
from src.extractor import extract_candidate_data

candidate = extract_candidate_data(resume_text)
# {"name": "John Doe", "skills": ["Python", "SQL"], "experience": 4, ...}
```

## Embeddings

`src/embedder.py` uses the `all-MiniLM-L6-v2` Sentence Transformers model to
generate normalized semantic vectors for a job description and each resume.
The model loads only when `generate_embeddings` is called.

```python
from src.embedder import generate_embeddings

resume_embeddings, jd_embedding = generate_embeddings(resume_texts, job_description)
```
