from typing import List, Dict, Optional
import openai
from pathlib import Path
import re
from app.core.settings import settings
from app.models.subtitle_model import SubtitleModel, SubtitleStatus
from sqlalchemy.orm import Session
from app.utils import dd


class TranslationService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4.1-mini"
    

    def translate_subtitle(self, subtitle: SubtitleModel, db: Session, hu_subtitle_path: str) -> bool:
        """Translate subtitle file to target language"""
        video_id = hu_subtitle_path.split(".")[0]
        print(f"video id: {video_id}")
        with open(f"{settings.SUBTITLES_DIR}/{subtitle.video_id}/{hu_subtitle_path}", 'r', encoding='utf-8') as f:
            content = f.read()
        print("content read, start translation")
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
            print("translation done, start writing")
            subtitle_path = f"{video_id}.{subtitle.language}.vtt"
            target_path = Path(f"{settings.SUBTITLES_DIR}/{subtitle.video_id}/{subtitle_path}")
            print("writing translated subtitles")
            # Write translated subtitles
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            print("writing done")
            subtitle.path = subtitle_path
            subtitle.status = SubtitleStatus.TRANSLATED
            db.add(subtitle)
            db.commit()
            print("subtitle updated")
            
        except Exception as e:
            print(f"Translation error: {e}")
            return False

        return True
    