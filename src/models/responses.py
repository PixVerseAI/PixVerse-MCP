"""
Pydantic models for Pixverse API responses.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video generation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoGenerationResponse(BaseModel):
    """Response model for video generation requests."""

    video_id: int
    status: VideoStatus = VideoStatus.PENDING
    
    # Fields from GetOpenapiMediaDetailResp (for get_video_result)
    id: Optional[int] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    resolution_ratio: Optional[int] = None
    url: Optional[str] = None  # video URL
    size: Optional[int] = None  # video file size
    seed: Optional[int] = None
    style: Optional[str] = None
    create_time: Optional[str] = None
    modify_time: Optional[str] = None
    outputWidth: Optional[int] = None
    outputHeight: Optional[int] = None
    has_audio: Optional[bool] = None
    customer_paths: Optional[Any] = None
    
    # Convenience properties for backward compatibility
    @property
    def video_url(self) -> Optional[str]:
        return self.url
    
    @property
    def width(self) -> Optional[int]:
        return self.outputWidth
        
    @property
    def height(self) -> Optional[int]:
        return self.outputHeight
        
    @property
    def file_size(self) -> Optional[int]:
        return self.size
        
    @property
    def duration(self) -> Optional[int]:
        # Duration is not directly available, but we can estimate from size
        return None


class ErrorResponse(BaseModel):
    """Error response model."""

    ErrCode: int
    ErrMsg: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    Resp: Optional[Dict[str, Any]] = None
    ErrCode: int = 0
    ErrMsg: str = "Success"


class LipSyncTTSInfo(BaseModel):
    """TTS speaker information for lip sync."""

    speaker_id: str
    name: str


class LipSyncTTSListResponse(BaseModel):
    """Response for TTS speaker list."""

    total: int
    data: list[LipSyncTTSInfo]


class VideoCreditsResponse(BaseModel):
    """Response for video credits information."""

    video_id: int
    credit: int


class MediaUploadResponse(BaseModel):
    """Response for media upload."""

    media_id: int = Field(alias="media_id")
    media_type: str = Field(alias="media_type")
    url: str = Field(alias="url")
    
    class Config:
        populate_by_name = True


class ImageUploadResponse(BaseModel):
    """Response for image upload."""

    img_id: int = Field(alias="ImgID")
    img_url: str = Field(alias="ImgUrl")
    
    class Config:
        populate_by_name = True
