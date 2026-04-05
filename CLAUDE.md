# CLAUDE.md — listify-rembg
> Instructions for Claude Code sessions on this project.
> This is a Python microservice. Read SPEC.md first.

---

## Project Identity

**listify-rembg** — Background removal microservice.
Single FastAPI app. Deployed on Hugging Face Spaces.
Called only by listify-apis — never by end users directly.

---

## What This Project Contains

Exactly 4 files:
1. `main.py` — the entire FastAPI service
2. `requirements.txt` — Python deps
3. `Dockerfile` — HF Space Docker deployment
4. `README.md` — HF Space metadata (YAML frontmatter required)

Nothing else. Do not add more files.

---

## Coding Rules

- Python 3.11+
- Type hints on all functions
- No external config files — all config is hardcoded constants or env vars read inline
- No database — this service is stateless
- No logging framework — print() is fine for HF Space logs
- Keep `main.py` under 80 lines

---

## The Only Two Endpoints

```
GET  /health     → {"status": "ok"}
POST /remove-bg  → PNG bytes
```

Do not add any other endpoints without explicit instruction.

---

## Error Handling

Use FastAPI HTTPException only. Never return 200 with an error body.

| Situation | Status | Detail |
|---|---|---|
| Wrong file type | 415 | "Unsupported format. Use JPEG, PNG, or WebP." |
| File too large | 413 | "File too large. Max 10MB." |
| rembg crashes | 500 | "Processing failed" |

---

## HF Space Constraints

- Must expose port 7860
- Dockerfile must use FROM python:3.11-slim
- README.md must have YAML frontmatter with sdk: docker
- First request after cold start downloads rembg ONNX model (~170MB) — expected, not a bug

---

## Session Workflow

1. Read SPEC.md
2. Read CLAUDE.md (this file)
3. Make changes
4. Confirm main.py is under 80 lines and all 4 files exist
5. Update TODO.md

---

## What NOT To Do

- Do not add API key auth — that is listify-apis' job
- Do not add rate limiting — that is listify-apis' job
- Do not add image storage — return bytes directly
- Do not add image resizing — not this service's job
- Do not add more endpoints
- Do not add a database connection
