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

## Similarity scoring

`src/scorer.py` calculates the cosine similarity between a resume vector and a
job-description vector, returning a percentage rounded to one decimal place.

```python
from src.scorer import calculate_similarity

similarity = calculate_similarity(jd_embedding, resume_embeddings["john.pdf"])
# 87.4
```

## Weighted scoring

The final candidate score combines semantic similarity, required-skill coverage,
and experience against the stated requirement:

```text
final score = 0.7 × similarity + 0.2 × skill match + 0.1 × experience
```

`src/scorer.py` exposes `calculate_skill_match`, `calculate_experience_score`,
and `calculate_weighted_score` for these components. When a job description
does not state a skill or experience requirement, that component receives 100%
so candidates are not penalized for a missing criterion.
