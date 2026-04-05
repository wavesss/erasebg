# TODO — listify-rembg

## Session 1 — Build and deploy to HF Space

### Goal
4 files created, deployed to HF Space, health check returning 200.

### Tasks

- [x] Create `main.py` — full FastAPI service per SPEC.md section 2
- [x] Create `requirements.txt` — exact versions from SPEC.md
- [x] Create `Dockerfile` — per SPEC.md section 2
- [x] Create `README.md` — with required HF Space YAML frontmatter

### Deploy checklist

- [ ] Push to GitHub repo `listify-rembg`
- [ ] Create HF Space (Docker sdk) connected to GitHub repo
- [ ] Wait for build to complete
- [ ] Run health check:
      curl https://YOUR-USERNAME-listify-rembg.hf.space/health
- [ ] Run remove-bg test:
      curl -X POST https://YOUR-USERNAME-listify-rembg.hf.space/remove-bg \
        -F "file=@/path/to/product.jpg" --output result.png
- [ ] Copy Space URL → add to listify-apis .env.local as REMBG_API_URL
- [ ] Add keep-warm cron to listify-apis (see SPEC.md section 3)

### Done when
- /health returns {"status":"ok"}
- /remove-bg returns a valid PNG with transparent background
- URL is set in listify-apis env and the /api/v1/remove endpoint works end-to-end
