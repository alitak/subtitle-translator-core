from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import os
from app.db.base import get_db
from app.schemas.resources.video_resource import VideoList, VideoResource
from app.schemas.requests.video_request import VideoCreateRequest
from app.models.video_model import VideoModel, VideoStatus
from app.models.subtitle_model import SubtitleModel
from app.utils import dd_http

router = APIRouter()
# task_manager = BackgroundTaskManager()


@router.get("/", response_model=VideoList)
def index(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(VideoModel)
    total = query.count()
    videos = query.order_by(VideoModel.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "items": videos,
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit
    }


@router.post("/", response_model=VideoResource, status_code=status.HTTP_201_CREATED)
def store(
    video: VideoCreateRequest,
    db: Session = Depends(get_db),
):
    video_obj = VideoModel(
        url=str(video.url),
        status=VideoStatus.PENDING
    )
    
    subtitles = []
    for lang in video.languages:
        subtitles.append(SubtitleModel(language=lang))

    video_obj.subtitles = subtitles

    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    
    # # Start background task for downloading subtitles
    # # task_id = f"download_subtitles_{db_video.id}"
    # # task_manager.create_task(
    # #     task_id=task_id,
    # #     task_func=service.download_subtitles,
    # #     video_id=str(db_video.id)
    # # )
    
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


# @router.post("/{video_id}/subtitles", status_code=status.HTTP_202_ACCEPTED)
# def translate_subtitles(
#     video_id: str,
#     subtitle: SubtitleCreate,
#     db: Session = Depends(get_db)
# ):
#     """Start translation of subtitles to the specified language"""
#     service = VideoService(db)
#     video = service.get_video(video_id)
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")
    
#     # Find source subtitle (prefer English as source)
#     source_sub = next((s for s in video.subtitles if s.language == 'en'), None)
#     if not source_sub:
#         source_sub = next((s for s in video.subtitles), None)
#         if not source_sub:
#             raise HTTPException(status_code=400, detail="No source subtitles available for translation")
    
#     # Check if translation already exists
#     existing_translation = next(
#         (s for s in video.subtitles if s.language == subtitle.language),
#         None
#     )
    
#     if existing_translation:
#         return {"status": "already_exists", "subtitle_id": existing_translation.id}
    
#     # Start background translation task
#     task_id = f"translate_{video_id}_{subtitle.language}"
#     task_manager.create_task(
#         task_id=task_id,
#         task_func=translate_subtitle_task,
#         video_id=video_id,
#         source_path=source_sub.path,
#         target_lang=subtitle.language,
#         db=db
#     )
    
#     return {"status": "translation_started", "task_id": task_id}

# def translate_subtitle_task(video_id: str, source_path: str, target_lang: str, db: Session):
#     """Background task to handle subtitle translation"""
#     from ...models.video import Subtitle
#     from ...services.video_service import VideoService
    
#     service = VideoService(db)
#     translation_service = TranslationService()
    
#     try:
#         # Translate the subtitle
#         target_path = translation_service.translate_subtitle(source_path, target_lang)
        
#         # Create subtitle record
#         subtitle = Subtitle(
#             video_id=video_id,
#             language=target_lang,
#             status="translated",
#             path=target_path
#         )
#         db.add(subtitle)
#         db.commit()
        
#         # Update video status if needed
#         video = service.get_video(video_id)
#         if video and video.status == "downloaded":
#             video.status = "translated"
#             db.commit()
            
#     except Exception as e:
#         print(f"Translation task failed: {e}")
#         raise
