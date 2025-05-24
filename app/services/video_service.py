import os
import yt_dlp
from app.utils import init_logging
from sqlalchemy.orm import Session
from ..models.video_model import VideoModel, VideoStatus
from ..models.subtitle_model import SubtitleStatus
from ..services.translation_service import TranslationService
from fastapi import BackgroundTasks

logger = init_logging("service.video")

class VideoService:
    def __init__(self, db: Session):
        self.db = db
        self.base_dir = "storage/subtitles"
        os.makedirs(self.base_dir, exist_ok=True)
    
    def download_subtitles(self, video: VideoModel, background_tasks: BackgroundTasks = None) -> bool:
        """Download subtitles for a video and update its metadata.
        
        Args:
            video: The video model to download subtitles for
            background_tasks: Optional BackgroundTasks instance for running translation tasks
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not video:
            return False

        logger.info(f"Starting subtitle download for video {video.id}")

        video.status = VideoStatus.DOWNLOADING
        self.db.commit()

        try:
            video_dir = os.path.join(self.base_dir, str(video.id))
            os.makedirs(video_dir, exist_ok=True)

            ydl_opts = {
                'skip_download': True,
                'writeautomaticsub': True,  # Download auto-generated subtitles
                'subtitleslangs': ['hu'],    # Only download Hungarian subtitles
                'subtitlesformat': 'vtt',    # Use VTT format (more reliable for auto-subs)
                'outtmpl': os.path.join(video_dir, '%(id)s.%(ext)s'),
                'quiet': True,               # Suppress output
                'noplaylist': True,          # Don't download playlists
                'ignoreerrors': True,         # Continue on errors
                'no_warnings': True           # Suppress warnings
            }

            logger.info("Using yt_dlp options: %s", ydl_opts)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video.url, download=True)
                
                if new_title := info.get('title'):
                    video.title = new_title
                    self.db.add(video)
                
                if video_id := info.get('id'):
                    if subtitle_hu := next((s for s in video.subtitles if s.language == 'hu'), None):
                        subtitle_hu.path = f"{video_id}.hu.vtt"
                        subtitle_hu.status = SubtitleStatus.TRANSLATED
                        self.db.add(subtitle_hu)

            logger.info("Subtitles downloaded successfully, updating database")

            video.status = VideoStatus.DOWNLOADED
            self.db.commit()

            logger.info("Starting background translation tasks")

            for subtitle in video.subtitles:
                if subtitle.language != "hu":
                    background_tasks.add_task(
                        TranslationService().translate_subtitle,
                        subtitle_id=subtitle.id,
                        video_id=video.id,
                        db=self.db,
                        hu_subtitle_path=subtitle_hu.path
                    )
            return True

        except Exception as e:
            video.status = VideoStatus.PENDING
            self.db.commit()
            raise e
