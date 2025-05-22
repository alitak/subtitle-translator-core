from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from .video import Video


class SubtitleStatus(str, enum.Enum):
    PENDING = "pending"
    TRANSLATED = "translated"


class Subtitle(BaseModel):
    __tablename__ = "subtitles"

    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(10), nullable=False)
    status = Column(Enum(SubtitleStatus), default=SubtitleStatus.PENDING, nullable=False)
    path = Column(Text, nullable=False)

    video = relationship("Video", back_populates="subtitles")
