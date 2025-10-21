"""
Pydantic models for Pixverse API requests.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import (
    AspectRatio,
    CameraMovement,
    Duration,
    FusionType,
    ImageId,
    ModelVersion,
    MotionMode,
    Seed,
    SoundMode,
    TemplateId,
    VideoId,
    VideoQuality,
    VideoStyle,
)


class SoundEffectInfo(BaseModel):
    """Sound effect configuration."""

    sound_effect_switch: bool = False
    sound_effect_content: Optional[str] = None
    sound_mode: Optional[SoundMode] = None

    @model_validator(mode="after")
    def validate_sound_content(self):
        if self.sound_effect_switch and self.sound_mode and self.sound_effect_content:
            raise ValueError("sound_effect_content and sound_mode cannot be used together")
        return self


class TextToVideoRequest(BaseModel):
    """Request model for text-to-video generation."""

    prompt: str = Field(..., max_length=2048, description="Text prompt for video generation")
    model: ModelVersion = Field(ModelVersion.V5, description="Model version to use")
    duration: Duration = Field(5, description="Video duration in seconds")
    aspect_ratio: AspectRatio = Field(AspectRatio.RATIO_16_9, description="Video aspect ratio")
    quality: VideoQuality = Field(VideoQuality.Q540P, description="Video quality")

    # Optional parameters
    negative_prompt: Optional[str] = Field(None, max_length=2048)
    seed: Optional[Seed] = None
    style: Optional[VideoStyle] = None
    motion_mode: Optional[MotionMode] = MotionMode.NORMAL
    camera_movement: Optional[CameraMovement] = None
    template_id: Optional[TemplateId] = None
    water_mark: bool = False
    play_bgm: bool = False

    # Sound effect
    sound_effect_switch: bool = False
    sound_effect_content: Optional[str] = Field(None, max_length=2048)
    sound_mode: Optional[SoundMode] = None

    @model_validator(mode="after")
    def validate_camera_movement_template(self):
        if self.camera_movement and self.template_id:
            raise ValueError("camera_movement cannot be used with template_id")
        return self


class ImageToVideoRequest(BaseModel):
    """Request model for image-to-video generation."""

    prompt: str = Field(..., max_length=2048, description="Text prompt for video generation")
    model: ModelVersion = Field(..., description="Model version to use")
    duration: Duration = Field(..., description="Video duration in seconds")
    quality: VideoQuality = Field(..., description="Video quality")

    # Image parameters (one of these is required)
    img_id: Optional[ImageId] = None
    img_ids: Optional[List[ImageId]] = None

    # Optional parameters
    negative_prompt: Optional[str] = Field(None, max_length=2048)
    seed: Optional[Seed] = None
    style: Optional[VideoStyle] = None
    template_id: Optional[TemplateId] = None
    motion_mode: Optional[MotionMode] = MotionMode.NORMAL
    camera_movement: Optional[CameraMovement] = None
    water_mark: bool = False
    play_bgm: bool = False

    # Sound effect
    sound_effect_switch: bool = False
    sound_effect_content: Optional[str] = Field(None, max_length=2048)
    sound_mode: Optional[SoundMode] = None

    @model_validator(mode="after")
    def validate_image_params(self):
        if not self.img_id and not self.img_ids:
            if not self.template_id:
                raise ValueError("Either img_id or img_ids must be provided when template_id is not set")
        if self.img_id and self.img_ids:
            raise ValueError("Cannot use both img_id and img_ids")
        return self


class TransitionVideoRequest(BaseModel):
    """Request model for transition video generation (first frame to last frame)."""

    prompt: str = Field(..., max_length=2048, description="Text prompt for video generation")
    first_frame_img: ImageId = Field(..., description="First frame image ID")
    last_frame_img: ImageId = Field(..., description="Last frame image ID")
    model: ModelVersion = Field(..., description="Model version (v3.5+)")
    duration: Duration = Field(..., description="Video duration in seconds")
    quality: VideoQuality = Field(..., description="Video quality")

    # Optional parameters
    negative_prompt: Optional[str] = Field(None, max_length=2048)
    seed: Optional[Seed] = None
    motion_mode: Optional[MotionMode] = MotionMode.NORMAL
    water_mark: bool = False
    play_bgm: bool = False

    # Sound effect
    sound_effect_switch: bool = False
    sound_effect_content: Optional[str] = Field(None, max_length=2048)
    sound_mode: Optional[SoundMode] = None


class ExtendVideoRequest(BaseModel):
    """Request model for video extension."""

    prompt: str = Field(..., max_length=2048, description="Text prompt for video extension")
    model: ModelVersion = Field(..., description="Model version (v3.5+)")
    duration: Duration = Field(..., description="Video duration in seconds")
    quality: VideoQuality = Field(..., description="Video quality")

    # Video source (one required)
    source_video_id: Optional[VideoId] = None
    video_media_id: Optional[VideoId] = None

    # Optional parameters
    negative_prompt: Optional[str] = Field(None, max_length=2048)
    seed: Optional[Seed] = None
    motion_mode: Optional[MotionMode] = MotionMode.NORMAL
    template_id: Optional[TemplateId] = None
    style: Optional[VideoStyle] = None

    @model_validator(mode="after")
    def validate_video_source(self):
        if not self.source_video_id and not self.video_media_id:
            raise ValueError("Either source_video_id or video_media_id must be provided")
        if self.source_video_id and self.video_media_id:
            raise ValueError("Cannot use both source_video_id and video_media_id")
        return self


class LipSyncVideoRequest(BaseModel):
    """Request model for lip sync video generation."""

    # Video source (one required)
    source_video_id: Optional[VideoId] = None
    video_media_id: Optional[VideoId] = None

    # Audio source (one group required)
    audio_media_id: Optional[int] = None
    lip_sync_tts_speaker_id: Optional[str] = None
    lip_sync_tts_content: Optional[str] = Field(None, max_length=200)

    @model_validator(mode="after")
    def validate_audio_source(self):
        # Validate video source
        if not self.source_video_id and not self.video_media_id:
            raise ValueError("Either source_video_id or video_media_id must be provided")
        if self.source_video_id and self.video_media_id:
            raise ValueError("Cannot use both source_video_id and video_media_id")

        # Validate audio source
        if not self.audio_media_id and not (self.lip_sync_tts_speaker_id and self.lip_sync_tts_content):
            raise ValueError(
                "Either audio_media_id or (lip_sync_tts_speaker_id + lip_sync_tts_content) must be provided"
            )
        if self.audio_media_id and (self.lip_sync_tts_speaker_id or self.lip_sync_tts_content):
            raise ValueError("Cannot use audio_media_id with TTS parameters")

        return self


class SoundEffectVideoRequest(BaseModel):
    """Request model for sound effect video generation."""

    sound_effect_content: str = Field(..., max_length=2048, description="Sound effect description")

    # Video source (one required)
    source_video_id: Optional[VideoId] = None
    video_media_id: Optional[VideoId] = None

    # Optional parameters
    original_sound_switch: bool = False
    seed: Optional[Seed] = None

    @model_validator(mode="after")
    def validate_video_source_sound(self):
        if not self.source_video_id and not self.video_media_id:
            raise ValueError("Either source_video_id or video_media_id must be provided")
        if self.source_video_id and self.video_media_id:
            raise ValueError("Cannot use both source_video_id and video_media_id")
        return self


class ImageReference(BaseModel):
    """Image reference for fusion video generation."""

    type: FusionType = Field(..., description="Reference type")
    img_id: ImageId = Field(..., description="Image ID")
    ref_name: str = Field(..., max_length=30, description="Reference name for prompt")

    @field_validator("ref_name")
    @classmethod
    def validate_ref_name(cls, v):
        import re

        if not re.match(r"^[a-zA-Z0-9_ ]+$", v):
            raise ValueError("ref_name must contain only alphanumeric characters, underscores, and spaces")
        return v


class FusionVideoRequest(BaseModel):
    """Request model for fusion video generation (multi-subject)."""

    image_references: List[ImageReference] = Field(..., min_length=1, max_length=3)
    prompt: str = Field(..., max_length=2048, description="Text prompt with @ref_name references")
    model: ModelVersion = Field(ModelVersion.V4_5, description="Model version (only v4.5 supported)")
    duration: Duration = Field(..., description="Video duration in seconds")
    quality: VideoQuality = Field(..., description="Video quality")
    aspect_ratio: AspectRatio = Field(..., description="Video aspect ratio")

    # Optional parameters
    negative_prompt: Optional[str] = Field(None, max_length=2048)
    seed: Optional[Seed] = None

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        if v != ModelVersion.V4_5:
            raise ValueError("Fusion generation only supports v4.5 model")
        return v

    @model_validator(mode="after")
    def validate_prompt_references(self):
        if not self.image_references:
            return self

        # Check that all ref_names in image_references are used in prompt
        ref_names = {ref.ref_name for ref in self.image_references}
        for ref_name in ref_names:
            if f"@{ref_name}" not in self.prompt:
                raise ValueError(f"Reference @{ref_name} not found in prompt")

        return self

    @field_validator("image_references")
    @classmethod
    def validate_unique_ref_names(cls, v):
        ref_names = [ref.ref_name for ref in v]
        if len(ref_names) != len(set(ref_names)):
            raise ValueError("All ref_names must be unique")
        return v
