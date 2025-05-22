# Import all models here so they're properly registered with SQLAlchemy
from .base import Base, BaseModel
from .video import Video, VideoStatus
from .subtitle import Subtitle, SubtitleStatus

# This ensures that all models are imported and registered with the Base metadata
__all__ = ['Base', 'BaseModel', 'Video', 'Subtitle', 'VideoStatus', 'SubtitleStatus']
