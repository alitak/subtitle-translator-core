from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class SubtitleStatus(str, enum.Enum):
    PENDING = "pending"
    TRANSLATING = "translating"
    TRANSLATED = "translated"


class SubtitleModel(BaseModel):
    __tablename__ = "subtitles"

    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(10), nullable=False)
    status = Column(Enum(SubtitleStatus), default=SubtitleStatus.PENDING, nullable=False)
    path = Column(Text, nullable=False)

    video = relationship("VideoModel", back_populates="subtitles")
