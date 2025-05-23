from pydantic import BaseModel
from app.models.subtitle_model import SubtitleStatus

class SubtitleRequest(BaseModel):
    language: str
    status: SubtitleStatus
    path: str

class SubtitleCreateRequest(SubtitleRequest):
    pass
