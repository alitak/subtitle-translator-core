from pydantic import BaseModel, HttpUrl
from typing import List

class VideoRequest(BaseModel):
    url: HttpUrl

class VideoCreateRequest(VideoRequest):
    languages: List[str]
