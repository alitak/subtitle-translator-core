from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.utils import register_debug_exception_handler
from .api.v1.endpoints import videos
from app.core.settings import settings

app = FastAPI(
    title="Subtitle Translator API",
    description="API for downloading and translating video subtitles",
    version="1.0.0"
)
register_debug_exception_handler(app)

app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

@app.get("/")
def read_root():
    return {"status": "ok"}
    

app.add_middleware(
    CORSMiddleware,
    # Development:
    allow_origins=["*"],
    # Production:
    # allow_origins=["https://sub.alitak.hu"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    videos.router,
    prefix="/api/v1/videos",
    tags=["videos"]
)

    # "openai==1.12.0",