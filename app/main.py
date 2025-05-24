from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.utils import register_debug_exception_handler, init_logging
from .api.v1.endpoints import videos
from app.core.settings import settings

logger = init_logging("main")
logger.info("FastAPI application starting up")

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
    

# List of allowed origins (frontend URLs)
origins = [
    "https://sub.alitak.hu",  # Production frontend
    "http://localhost:5173",   # Local development
    "http://127.0.0.1:5173",   # Local development alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(
    videos.router,
    prefix="/api/v1/videos",
    tags=["videos"]
)
