from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from app.models.video_model import VideoStatus
from app.schemas.resources.subtitle_resource import SubtitleResource

class VideoResource(BaseModel):
    id: str
    url: HttpUrl
    title: Optional[str] = None
    status: VideoStatus
    subtitles: List[SubtitleResource] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VideoList(BaseModel):
    items: List[VideoResource]
    total: int
    page: int
    limit: int
