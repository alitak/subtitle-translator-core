from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class VideoStatus(str, enum.Enum):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    DOWNLOADED = 'downloaded'

class VideoModel(BaseModel):
    __tablename__ = 'videos'
    
    url = Column(String(512), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING, nullable=False)
    
    subtitles = relationship("SubtitleModel", back_populates="video", cascade="all, delete-orphan")
