# Import all models here so they're properly registered with SQLAlchemy
from .base import Base, BaseModel
from .video_model import VideoModel, VideoStatus
from .subtitle_model import SubtitleModel, SubtitleStatus

# This ensures that all models are imported and registered with the Base metadata
__all__ = ['Base', 'BaseModel', 'VideoModel', 'SubtitleModel', 'VideoStatus', 'SubtitleStatus']
