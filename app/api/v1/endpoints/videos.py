from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
import os
from app.utils import init_logging
from app.db.base import get_db
from app.schemas.resources.video_resource import VideoList, VideoResource
from app.schemas.requests.video_request import VideoCreateRequest
from app.models.video_model import VideoModel, VideoStatus
from app.models.subtitle_model import SubtitleModel
from app.services.video_service import VideoService
from app.services.translation_service import TranslationService
from app.core.settings import settings
from app.utils import dd_http

logger = init_logging("api.videos")

router = APIRouter()


@router.get("/", response_model=VideoList)
def index(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.info("Fetching video list from database")
    query = db.query(VideoModel)
    total = query.count()
    videos = query.order_by(VideoModel.created_at.desc()).offset(skip).limit(limit).all()

    # Update subtitle paths to use the correct URL
    for video in videos:
        for subtitle in video.subtitles:
            if subtitle.path:
                subtitle.path = f"{settings.BASE_URL}/storage/subtitles/{video.id}/{subtitle.path}"

    return {
        "items": videos,
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit
    }


@router.post("/", response_model=VideoResource, status_code=status.HTTP_201_CREATED)
def store(
    video: VideoCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    logger.info(f"Storing new video with URL: {video.url}")
    video_obj = VideoModel(
        url=str(video.url),
        status=VideoStatus.PENDING
    )
    subtitles = []
    video.languages.insert(0, "hu")
    for lang in video.languages:
        subtitles.append(SubtitleModel(language=lang))

    video_obj.subtitles = subtitles

    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    
    background_tasks.add_task(
        VideoService(db).download_subtitles,
        video_obj,
        background_tasks
    )
    
    return video_obj


# @router.get("/{video_id}", response_model=VideoResource)
# def show(
#     video_id: str,
#     db: Session = Depends(get_db)
# ):
#     video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")

#     return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(
    video_id: str,
    db: Session = Depends(get_db)
):
    logger.info(f"Deleting video with ID: {video_id}")
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Delete subtitle files
    video_dir = os.path.join("storage/subtitles", str(video_id))
    if os.path.exists(video_dir):
        for file in os.listdir(video_dir):
            os.remove(os.path.join(video_dir, file))
        os.rmdir(video_dir)
    
    db.delete(video)
    db.commit()

    return None


@router.post("/{video_id}/subtitles/{language}", status_code=status.HTTP_202_ACCEPTED)
def translate_subtitles(
    video_id: str,
    language: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    logger.info(f"Request received to translate video {video_id} to {language}")
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    source_sub = next((s for s in video.subtitles if s.language == "hu"), None)
    if not source_sub:
        raise HTTPException(
            status_code=400, 
            detail=f"No source subtitles available in language 'hu' for translation"
        )
    
    subtitle = next((s for s in video.subtitles if s.language == language), None)

    if not subtitle:
        subtitle = SubtitleModel(language=language)
        video.subtitles.append(subtitle)
        db.add(video)
        db.commit()
    
    background_tasks.add_task(
        TranslationService().translate_subtitle,
        subtitle_id=subtitle.id,
        video_id=video.id,
        db=db,
        hu_subtitle_path=source_sub.path
    )
    
    return {"status": "translation_started"}
