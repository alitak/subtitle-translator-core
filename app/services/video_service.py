import os
import yt_dlp
from sqlalchemy.orm import Session
from ..models.video_model import VideoModel, VideoStatus
from ..models.subtitle_model import SubtitleStatus

class VideoService:
    def __init__(self, db: Session):
        self.db = db
        self.base_dir = "storage/subtitles"
        os.makedirs(self.base_dir, exist_ok=True)
    
    def download_subtitles(self, video: VideoModel) -> bool:
        """Download subtitles for a video and update its metadata.
        
        Args:
            video: The video model to download subtitles for
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not video:
            return False

        video.status = VideoStatus.DOWNLOADING
        self.db.commit()

        try:
            # Create video directory
            video_dir = os.path.join(self.base_dir, str(video.id))
            os.makedirs(video_dir, exist_ok=True)

            # Configure yt-dlp options
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

            # Download subtitles and get video info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video.url, download=True)
                
                # Update video title if available
                if new_title := info.get('title'):
                    video.title = new_title
                    self.db.add(video)
                
                # Get the subtitle filename
                if video_id := info.get('id'):
                    subtitle_filename = f"{video_id}.hu.vtt"
                    
                    # Update the subtitle record
                    if subtitle := next((s for s in video.subtitles if s.language == 'hu'), None):
                        subtitle.path = subtitle_filename
                        subtitle.status = SubtitleStatus.TRANSLATED
                        self.db.add(subtitle)

            # Update status and commit changes
            video.status = VideoStatus.DOWNLOADED
            self.db.commit()
            return True

        except Exception as e:
            video.status = VideoStatus.PENDING
            self.db.commit()
            raise e
