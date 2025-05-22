from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from .subtitle import Subtitle

class VideoStatus(str, enum.Enum):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    DOWNLOADED = 'downloaded'

class Video(BaseModel):
    __tablename__ = 'videos'
    
    url = Column(String(512), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING, nullable=False)
    
    subtitles = relationship("Subtitle", back_populates="video", cascade="all, delete-orphan")
