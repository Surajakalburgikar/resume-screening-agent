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
text keyed by the original file name. It keeps meaningful line breaks for later
field extraction, while normalizing inline whitespace. Non-PDF files are ignored.

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

## Ranking

`src/ranker.py` sorts candidate records by `final_score` and returns copied
records with a 1-based `rank`. Equal scores are ordered by candidate name for
consistent results.

```python
from src.ranker import rank_candidates

ranked_candidates = rank_candidates(candidates)
# [{"name": "John", "final_score": 91.0, "rank": 1}, ...]
```

## Match reasons

`src/report.py` produces an evidence-based explanation for each candidate. It
lists skills matched against the job description, missing skills, and whether
their stated experience meets the requirement.

```python
from src.report import generate_match_reason

reason = generate_match_reason(candidate, required_skills, required_experience=3)
# {"matched_skills": ["Python"], "missing_skills": ["AWS"], "reason": "..."}
```

## Export rankings

`export_rankings` writes the final ranked candidate records to the required
`output/rankings.csv` and `output/rankings.json` files. JSON retains nested
lists; CSV converts them to comma-separated text for easy review.

```python
from src.report import export_rankings

csv_path, json_path = export_rankings(ranked_candidates)
```

## Streamlit app

Run the complete screening interface with:

```bash
streamlit run app.py
```

The app accepts a pasted job description and PDF resume uploads. It shows a
progress indicator, ranked candidates, top five matching skills, missing skills,
minimum-score filtering, candidate details, and CSV/JSON downloads. It also
writes the latest reports to `output/rankings.csv` and `output/rankings.json`.
