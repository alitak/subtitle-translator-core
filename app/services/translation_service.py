from typing import List, Dict, Optional
import openai
from pathlib import Path
import re
from app.core.settings import settings
from app.models.subtitle_model import SubtitleModel, SubtitleStatus
from sqlalchemy.orm import Session
from app.utils import dd
from app.utils import init_logging


class TranslationService:
    logger = init_logging("translation_service")

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4.1-mini"
        self.logger = self.logger
    

    def translate_subtitle(self, subtitle_id: int, video_id: int, db: Session, hu_subtitle_path: str) -> bool:
        """Translate subtitle file to target language"""
        subtitle = db.query(SubtitleModel).filter(SubtitleModel.id == subtitle_id).first()
        self.logger.info(f"{video_id}, subtitle id: {subtitle_id}")
        with open(f"{settings.SUBTITLES_DIR}/{video_id}/{hu_subtitle_path}", 'r', encoding='utf-8') as f:
            content = f.read()
        self.logger.info(f"{video_id}, content read, start translation")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a professional subtitle translator. "
                            f"Translate the following text into {subtitle.language}. "
                            "The input is subtitle lines without timestamps. "
                            "Keep the line breaks as they reflect subtitle segmentation. "
                            "Do not add or remove anything beyond the translation."
                        ),
                    },
                    {"role": "user", "content": content}
                ],
                temperature=0.3,
            )
            translated_content = response.choices[0].message.content
            self.logger.info(f"{video_id}, translation done, start writing")
            subtitle_path = f"{video_id}.{subtitle.language}.vtt"
            target_path = Path(f"{settings.SUBTITLES_DIR}/{video_id}/{subtitle_path}")
            self.logger.info(f"{video_id}, writing translated subtitles")
            # Write translated subtitles
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            self.logger.info(f"{video_id}, writing done")
            subtitle.path = subtitle_path
            subtitle.status = SubtitleStatus.TRANSLATED
            db.add(subtitle)
            db.commit()
            self.logger.info(f"{video_id}, subtitle updated")
            
        except Exception as e:
            self.logger.error(f"{video_id}, Translation error: {e}")
            return False

        return True
