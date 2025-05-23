from app.models.subtitle_model import SubtitleStatus
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class SubtitleResource(BaseModel):
    id: str
    video_id: str
    status: SubtitleStatus
    language: str
    path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubtitleList(BaseModel):
    items: List[SubtitleResource]
    total: int
    page: int
    limit: int
    