from fastapi import FastAPI, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import io

app = FastAPI(title="listify-rembg", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported format. Use JPEG, PNG, or WebP."
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")

    try:
        output = remove(contents)
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")

    return Response(
        content=output,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=result.png"}
    )
