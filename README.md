# Evidence Desk

Find evidence. Show the source. Abstain when coverage is weak.

A local document-question answering service combining TF-IDF, BM25 and reciprocal-rank fusion. Answers are extracted from source sentences and include exact quotes and chunk identifiers. No paid API, external document transmission or language model is required.

**Status:** locally tested portfolio prototype, October 2026. Built with AI assistance; intended for hands-on study, review and extension. Not paid employment or a deployed commercial system.

## Quick start

Python 3.12 is the tested version. Dependencies are pinned to the locally tested environment.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python evaluate.py
python -m pytest -q
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the interactive demo, or /docs for API documentation.

```bash
curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" --data-binary @sample_request.json
```

Windows PowerShell alternative:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/answer -Method Post -ContentType application/json -Body (Get-Content sample_request.json -Raw)
```

## Architecture

```text
Documents → word chunks → TF-IDF and BM25 → rank fusion → coverage gate → quoted answer
```

- `core.py`: algorithms and validation, separate from transport.
- `app.py`: bounded Pydantic inputs, health endpoint and FastAPI interface.
- `test_core.py`: algorithm invariants, failure cases and API behavior.
- `evaluation.json`: actual saved local evaluation output; regenerate with the command above.
- `LEARNING_GUIDE.md`: walkthrough, interview questions and a practical extension exercise.
- `Dockerfile`: non-root container configuration. Docker execution has not been verified locally.
- `.github/workflows/ci.yml`: active automated evaluation and tests; first Linux run passed on 14 October 2026.

## Measured local results

On six handcrafted regression examples, five decisions matched the expected answer/abstention; top-1 retrieval found the correct document for all four answerable cases in each retrieval mode. One answerable query was conservatively refused. This tiny fixture is a development diagnostic, not evidence of generalization or superiority of hybrid search.

## Limitations and deployment boundary

Lexical matching can miss paraphrases; coverage is a heuristic rather than calibrated uncertainty. Exact quotation prevents invented wording but does not establish truth, relevance or safety of the underlying source. A malicious instruction may still appear in a retrieved quote, but the program never executes it. The API rebuilds the index per request and is intended for small local corpora.

Local demo only: no authentication, tenant isolation, persistence, TLS, rate limiter or deployment hardening is included. Bind to localhost for use. Request-size and field validation do not replace gateway body-size limits. Do not expose the service publicly without adding these controls. No credentials or personal data are needed.

## Design references

- [FastAPI container deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [scikit-learn model persistence considerations](https://scikit-learn.org/stable/model_persistence.html)
- [scikit-learn Wine dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html)

MIT license covers this code. The Wine dataset follows the source dataset's terms; synthetic images and example policies are generated fixtures. No patient data is included.

