from fastapi import FastAPI # , Depends
from fastapi.middleware.cors import CORSMiddleware
from app.utils import register_debug_exception_handler
# from sqlalchemy.orm import Session
# import os
# from pathlib import Path
from .api.v1.endpoints import videos

app = FastAPI(
    title="Subtitle Translator API",
    description="API for downloading and translating video subtitles",
    version="1.0.0"
)
register_debug_exception_handler(app)

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

    # "uvicorn==0.27.0",
    # "python-multipart==0.0.9",
    # "pydantic==2.6.1",
    # "pydantic-settings==2.1.0",
    # "python-jose[cryptography]==3.3.0",
    # "passlib[bcrypt]==1.7.4",
    # "yt-dlp==2024.3.10",
    # "openai==1.12.0",
    # "python-slugify==8.0.1",
    # "python-magic==0.4.27",