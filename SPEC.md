# SPEC.md — listify-rembg
> FastAPI microservice for background removal.
> Deployed on Hugging Face Spaces (free CPU tier).
> Called by listify-apis — never called directly by end users.

---

## 0. Overview

**Project name:** listify-rembg
**Type:** Python FastAPI app
**Deploy:** Hugging Face Spaces (free CPU)
**Called by:** `listify-apis` `/api/v1/remove` route only
**Direct public access:** None — HF Space URL is kept private via env var

This is a single-purpose microservice. It does one thing:
receive an image → remove background → return PNG.

---

## 1. Project Structure

```
listify-rembg/
├── main.py           # FastAPI app — the entire service
├── requirements.txt  # Python dependencies
└── README.md         # HF Space metadata (title, sdk, etc.)
```

That's it. No subdirectories. No config files. Minimal.

---

## 2. The Service

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}` — used by keep-warm cron |
| POST | `/remove-bg` | Accepts image file, returns PNG with transparent background |

### Full implementation

```python
# main.py
from fastapi import FastAPI, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import io

app = FastAPI(title="listify-rembg", version="1.0.0")

# Allow calls from listify-apis Vercel domain only
# In production: restrict origins to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this after deploy
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

SUPPORTED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile) -> Response:
    # Validate content type
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported format: {file.content_type}. Use JPEG, PNG, or WebP."
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")

    # Remove background
    try:
        output = remove(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return Response(
        content=output,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=result.png"}
    )
```

### Requirements

```
# requirements.txt
fastapi==0.111.0
uvicorn==0.30.1
rembg==2.0.57
python-multipart==0.0.9
onnxruntime==1.18.0
Pillow==10.3.0
```

### HF Space README (required metadata)

```yaml
---
title: listify-rembg
emoji: 🖼️
colorFrom: gray
colorTo: gray
sdk: docker
pinned: false
---
```

> Note: HF Spaces with FastAPI need to use the Docker sdk, not gradio.
> The Space will auto-detect `main.py` and run uvicorn.

### Dockerfile (required for Docker sdk on HF Spaces)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 7860

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "7860"]
```

> HF Spaces Docker apps must expose port 7860.

---

## 3. Keep-Warm Strategy

HF Spaces on free tier sleep after ~15 minutes of inactivity.
First request after sleep takes ~30 seconds (cold start). Unacceptable for an API.

**Solution:** Vercel cron in `listify-apis` pings `/health` every 4 minutes.

```json
// vercel.json in listify-apis
{
  "crons": [
    {
      "path": "/api/cron/ping-rembg",
      "schedule": "*/4 * * * *"
    }
  ]
}
```

```typescript
// src/app/api/cron/ping-rembg/route.ts in listify-apis
export async function GET() {
  const res = await fetch(`${process.env.REMBG_API_URL}/health`)
  const data = await res.json()
  return Response.json({ pinged: true, status: data.status })
}
```

This keeps the Space warm at zero cost.

---

## 4. Deployment Steps

### First deploy

1. Create new repo: `listify-rembg` on GitHub
2. Create new HF Space:
   - Go to huggingface.co/spaces → New Space
   - SDK: Docker
   - Visibility: Public (URL stays private via env var in listify-apis)
3. Connect GitHub repo to HF Space (auto-deploys on push)
4. Wait for build (~3–5 min first time, rembg model downloads on first request)
5. Copy the Space URL: `https://YOUR-USERNAME-listify-rembg.hf.space`
6. Add to `listify-apis` `.env.local`:
   ```
   REMBG_API_URL=https://YOUR-USERNAME-listify-rembg.hf.space
   ```

### Test after deploy

```bash
# Health check
curl https://YOUR-USERNAME-listify-rembg.hf.space/health
# Expected: {"status":"ok"}

# Background removal (direct test — bypasses listify-apis auth)
curl -X POST https://YOUR-USERNAME-listify-rembg.hf.space/remove-bg \
  -F "file=@/path/to/product.jpg" \
  --output result.png
open result.png
```

---

## 5. Scale Path

| Volume | Action | Cost |
|---|---|---|
| < 500 calls/day | HF Space free tier | €0 |
| 500–5000 calls/day | HF Space (may need Pro) or Hetzner CX11 | €5–10/month |
| > 5000 calls/day | Hetzner CX21 + nginx + multiple workers | ~€15/month |

**Migration is zero-code:** just update `REMBG_API_URL` in listify-apis env vars.

---

## 6. What This Service Does NOT Do

- No API key auth (handled by listify-apis)
- No rate limiting (handled by listify-apis)
- No usage tracking (handled by listify-apis)
- No storage (returns bytes directly, caller handles storage)
- No image resizing (handled by listify-apis if needed)
