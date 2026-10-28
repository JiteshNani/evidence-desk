# Evidence Desk

A small document search service that shows its evidence and refuses some questions it cannot support.

The project uses TF-IDF, BM25 and reciprocal-rank fusion to find relevant passages. It returns an exact sentence from a source document with its chunk ID. There is no language model or paid API in this version.

**Context:** an AI-assisted portfolio learning project, started in October 2026 and tested locally. This is separate from my paid employment.

## Why this project

A search result is not enough to justify an answer. I wanted a small system where I could inspect the retrieved passage, compare retrieval methods and see when an abstention rule fails. The implementation is deliberately simple so the decisions are visible.

## Run it locally

Python 3.12 is the tested version.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python evaluate.py
python evaluate_suite.py
python -m pytest -q
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the demo and /docs for the API.

```bash
curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" --data-binary @sample_request.json
```

PowerShell:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/answer -Method Post -ContentType application/json -Body (Get-Content sample_request.json -Raw)
```

## How it works

Documents → overlapping word chunks → TF-IDF and BM25 → rank fusion → query coverage gate → source sentence and citation.

- `core.py`: retrieval, validation and extractive answering.
- `app.py`: FastAPI endpoints with bounded request fields.
- `test_core.py`: citation, validation, abstention and API checks.
- `evaluate_suite.py`: development-only threshold selection, retrieval ablations, challenge breakdowns and answer-path latency.
- `evaluation_suite.json`: six example policy documents, 12 development queries and 16 separate test queries.
- `test_evaluation_suite.py`: five checks for ranking metrics and duplicate-chunk handling.
- `evaluation_suite_results.json`: saved output from the expanded local evaluation.
- `LEARNING_GUIDE.md`: walkthrough and exercises.
- `Dockerfile`: container configuration; Docker execution has not been verified.
- `.github/workflows/ci.yml`: automated evaluation and tests.

## What the evaluation actually shows

The original six-query fixture produced five correct source/abstention decisions.

The expanded suite selects the coverage threshold from **12 development queries**, then reports **16 separate regression queries**. It compares TF-IDF, BM25 and hybrid retrieval using document-level Recall@3, MRR@3 and nDCG@3. Repeated chunks from one document are deduplicated, using up to ten retrieved chunks before taking three document IDs.

In the saved run, threshold **0.5** produced **14/16 correct source-or-abstention decisions**, with **two false acceptances** on unanswerable questions sharing words with the corpus. All three retrieval methods scored equally on the small answerable fixture. There is no evidence here that hybrid search is better.

There are **13 passing local tests**. The fixture was written with AI assistance and is not a blinded benchmark. The query split helps keep threshold selection separate from the reported regression cases; it does not establish real-world generalization.

A correct source is not necessarily a correct answer. The scorer checks source identity or abstention, not entailment, completeness or whether a quotation resolves a negation. A multi-document question may retrieve both sources while the answer still quotes only one sentence. Reported latency covers the warm local answer path, excluding index creation, network calls and LLM inference.

## Remaining problems

Lexical matching can miss paraphrases. Coverage is a heuristic, not a calibrated confidence score. The service does not resolve conflicting policies or synthesize multiple sources. Exact quotations preserve source wording but cannot establish that the source itself is correct.

The API rebuilds its index per request and is intended for small local corpora. The demo has no authentication, tenant isolation, persistence, TLS or gateway rate limiting; use localhost. Document text is treated as data and never executed.

The next useful step is a broader, independently reviewed query set and an answer-correctness rubric. Embeddings or a reranker should be compared against these baselines before claiming an improvement.

## References and data

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)

MIT license covers the code. The example policies are generated fixtures. No patient, employer or customer documents are included.
