from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session

_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _session
    try:
        print("Loading isnet-general-use model...")
        _session = new_session("isnet-general-use")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"ERROR loading isnet-general-use: {e}")
        print("Falling back to u2net")
        _session = new_session("u2net")
    yield

app = FastAPI(title="listify-rembg", version="1.0.0", lifespan=lifespan)

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
        session = _session if _session is not None else new_session("isnet-general-use")
        output = remove(contents, session=session)
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")

    return Response(
        content=output,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=result.png"}
    )
