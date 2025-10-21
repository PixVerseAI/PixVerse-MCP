"""
Main Pixverse API client.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from ..exceptions import PixverseValidationError
from ..models.requests import (
    ExtendVideoRequest,
    FusionVideoRequest,
    ImageToVideoRequest,
    LipSyncVideoRequest,
    SoundEffectVideoRequest,
    TextToVideoRequest,
    TransitionVideoRequest,
)
from ..models.responses import (
    ImageUploadResponse,
    LipSyncTTSListResponse,
    MediaUploadResponse,
    VideoCreditsResponse,
    VideoGenerationResponse,
    VideoStatus,
)
from .base import BaseClient


class PixverseClient(BaseClient):
    """Main client for Pixverse video generation APIs."""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize Pixverse client.

        Args:
            api_key: Pixverse API key
            **kwargs: Additional arguments passed to BaseClient
        """
        super().__init__(api_key, **kwargs)
        logger.info("Pixverse client initialized")

    async def text_to_video(self, request: TextToVideoRequest) -> VideoGenerationResponse:
        """
        Generate video from text prompt.

        Args:
            request: Text-to-video request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Generating video from text: {request.prompt[:50]}...")

        response_data = await self.post(
            "/openapi/v2/video/text/generate",
            data=request.dict(exclude_none=True),
        )

        # Extract video_id from response
        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def image_to_video(self, request: ImageToVideoRequest) -> VideoGenerationResponse:
        """
        Generate video from image.

        Args:
            request: Image-to-video request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Generating video from image: {request.img_id or request.img_ids}")

        response_data = await self.post(
            "/openapi/v2/video/img/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def transition_video(self, request: TransitionVideoRequest) -> VideoGenerationResponse:
        """
        Generate transition video between two frames.

        Args:
            request: Transition video request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Generating transition video: {request.first_frame_img} -> {request.last_frame_img}")

        response_data = await self.post(
            "/openapi/v2/video/transition/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def extend_video(self, request: ExtendVideoRequest) -> VideoGenerationResponse:
        """
        Extend an existing video.

        Args:
            request: Video extension request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Extending video: {request.source_video_id or request.video_media_id}")

        response_data = await self.post(
            "/openapi/v2/video/extend/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def lip_sync_video(self, request: LipSyncVideoRequest) -> VideoGenerationResponse:
        """
        Generate lip sync video.

        Args:
            request: Lip sync request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Generating lip sync video: {request.source_video_id or request.video_media_id}")

        response_data = await self.post(
            "/openapi/v2/video/lip_sync/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def sound_effect_video(self, request: SoundEffectVideoRequest) -> VideoGenerationResponse:
        """
        Add sound effects to video.

        Args:
            request: Sound effect request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Adding sound effects to video: {request.source_video_id or request.video_media_id}")

        response_data = await self.post(
            "/openapi/v2/video/sound_effect/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def fusion_video(self, request: FusionVideoRequest) -> VideoGenerationResponse:
        """
        Generate fusion video with multiple subjects.

        Args:
            request: Fusion video request parameters

        Returns:
            Video generation response
        """
        logger.info(f"Generating fusion video with {len(request.image_references)} subjects")

        response_data = await self.post(
            "/openapi/v2/video/fusion/generate",
            data=request.dict(exclude_none=True),
        )

        resp_data = response_data.get("Resp", {})
        video_id = resp_data.get("video_id")

        if not video_id:
            raise PixverseValidationError("No video_id in response")

        return VideoGenerationResponse(video_id=video_id)

    async def get_lip_sync_tts_list(self, page_num: int = 1, page_size: int = 30) -> LipSyncTTSListResponse:
        """
        Get list of available TTS speakers for lip sync.

        Args:
            page_num: Page number (default: 1)
            page_size: Page size (default: 30)

        Returns:
            TTS speakers list response
        """
        logger.info("Getting TTS speakers list")

        params = {
            "page_num": page_num,
            "page_size": page_size,
        }

        response_data = await self.get(
            "/openapi/v2/video/lip_sync/tts_list",
            params=params,
        )

        resp_data = response_data.get("Resp", {})
        return LipSyncTTSListResponse(**resp_data)

    async def get_video_result(self, video_id: int) -> VideoGenerationResponse:
        """
        Get video generation result and status.

        Args:
            video_id: Video ID

        Returns:
            Video generation response with current status
        """
        logger.info(f"Getting result for video: {video_id}")

        response_data = await self.get(f"/openapi/v2/video/result/{video_id}")

        resp_data = response_data.get("Resp", {})
        
        # Map Go response fields to our model
        # Status mapping: 1=normal(completed), 6=deleted, 7=banned, 8=failed, 2=pending, 3=in_progress
        status_map = {
            1: VideoStatus.COMPLETED,
            2: VideoStatus.PENDING, 
            3: VideoStatus.IN_PROGRESS,
            6: VideoStatus.CANCELLED,
            7: VideoStatus.FAILED,
            8: VideoStatus.FAILED,
        }
        
        go_status = resp_data.get("status", 2)  # Default to pending
        mapped_status = status_map.get(go_status, VideoStatus.PENDING)
        
        return VideoGenerationResponse(
            video_id=video_id,
            status=mapped_status,
            id=resp_data.get("id"),
            prompt=resp_data.get("prompt"),
            negative_prompt=resp_data.get("negative_prompt"),
            resolution_ratio=resp_data.get("resolution_ratio"),
            url=resp_data.get("url"),
            size=resp_data.get("size"),
            seed=resp_data.get("seed"),
            style=resp_data.get("style"),
            create_time=resp_data.get("create_time"),
            modify_time=resp_data.get("modify_time"),
            outputWidth=resp_data.get("outputWidth"),
            outputHeight=resp_data.get("outputHeight"),
            has_audio=resp_data.get("has_audio"),
            customer_paths=resp_data.get("customer_paths")
        )

    async def get_video_credits(self, video_id: int) -> VideoCreditsResponse:
        """
        Get credits information for a video.

        Args:
            video_id: Video ID

        Returns:
            Video credits response
        """
        logger.info(f"Getting credits for video: {video_id}")

        response_data = await self.get(f"/video/credits/{video_id}")

        resp_data = response_data.get("Resp", {})
        return VideoCreditsResponse(**resp_data)

    async def upload_image(self, file_path: str = None, image_url: str = None) -> ImageUploadResponse:
        """
        Upload image file or from URL.

        Args:
            file_path: Path to the image file (for multipart upload)
            image_url: URL of the image (for form/json upload)

        Returns:
            Image upload response with img_id
        """
        if not file_path and not image_url:
            raise ValueError("Either file_path or image_url must be provided")
        
        if file_path and image_url:
            raise ValueError("Only one of file_path or image_url should be provided")

        if file_path:
            # Multipart upload for local file
            logger.info(f"Uploading image file: {file_path}")
            response_data = await self.upload_file(
                "/openapi/v2/image/upload",
                file_path=file_path,
                field_name="image"
            )
        else:
            # Form upload for URL
            logger.info(f"Uploading image from URL: {image_url}")
            response_data = await self.post(
                "/openapi/v2/image/upload",
                data={"image_url": image_url},
                use_form_data=True
            )

        resp_data = response_data.get("Resp", {})
        return ImageUploadResponse(**resp_data)

    async def upload_media(self, file_path: str = None, file_url: str = None, media_type: str = "video") -> MediaUploadResponse:
        """
        Upload media file (video/audio) or from URL.

        Args:
            file_path: Path to the media file (for multipart upload)
            file_url: URL of the media file (for form/json upload)
            media_type: Type of media (video, audio)

        Returns:
            Media upload response with media_id
        """
        if not file_path and not file_url:
            raise ValueError("Either file_path or file_url must be provided")
        
        if file_path and file_url:
            raise ValueError("Only one of file_path or file_url should be provided")

        if file_path:
            # Multipart upload for local file
            logger.info(f"Uploading {media_type} file: {file_path}")
            additional_data = {"media_type": media_type}
            response_data = await self.upload_file(
                "/openapi/v2/media/upload",
                file_path=file_path,
                field_name="file",
                additional_data=additional_data
            )
        else:
            # Form upload for URL
            logger.info(f"Uploading {media_type} from URL: {file_url}")
            response_data = await self.post(
                "/openapi/v2/media/upload",
                data={"file_url": file_url},
                use_form_data=True
            )

        resp_data = response_data.get("Resp", {})
        return MediaUploadResponse(**resp_data)

    # Convenience methods for common use cases

    async def quick_text_video(
        self,
        prompt: str,
        model: str = "v5",
        duration: int = 5,
        quality: str = "540p",
        aspect_ratio: str = "16:9",
        **kwargs,
    ) -> VideoGenerationResponse:
        """
        Quick text-to-video generation with sensible defaults.

        Args:
            prompt: Text prompt
            model: Model version (default: v5)
            duration: Video duration (default: 5)
            quality: Video quality (default: 540p)
            aspect_ratio: Aspect ratio (default: 16:9)
            **kwargs: Additional parameters

        Returns:
            Video generation response
        """
        request = TextToVideoRequest(
            prompt=prompt, model=model, duration=duration, quality=quality, aspect_ratio=aspect_ratio, **kwargs
        )
        return await self.text_to_video(request)

    async def quick_image_video(
        self, img_id: int, prompt: str, model: str = "v5", duration: int = 5, quality: str = "540p", **kwargs
    ) -> VideoGenerationResponse:
        """
        Quick image-to-video generation with sensible defaults.

        Args:
            img_id: Image ID
            prompt: Text prompt
            model: Model version (default: v5)
            duration: Video duration (default: 5)
            quality: Video quality (default: 540p)
            **kwargs: Additional parameters

        Returns:
            Video generation response
        """
        request = ImageToVideoRequest(
            img_id=img_id, prompt=prompt, model=model, duration=duration, quality=quality, **kwargs
        )
        return await self.image_to_video(request)

    async def wait_for_video_completion(
        self,
        video_id: int,
        max_wait_time: int = 300,
        poll_interval: int = 10,
    ) -> VideoGenerationResponse:
        """
        Wait for video generation to complete by polling status.

        Args:
            video_id: Video ID to monitor
            max_wait_time: Maximum wait time in seconds (default: 300)
            poll_interval: Polling interval in seconds (default: 10)

        Returns:
            Final video generation response

        Raises:
            PixverseTimeoutError: If video doesn't complete within max_wait_time
            PixverseAPIError: If video generation fails
        """
        import asyncio
        from ..exceptions import PixverseTimeoutError, PixverseAPIError

        logger.info(f"Waiting for video {video_id} to complete (max {max_wait_time}s)")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            result = await self.get_video_result(video_id)
            
            if result.status == VideoStatus.COMPLETED:
                logger.info(f"Video {video_id} completed successfully")
                return result
            elif result.status == VideoStatus.FAILED:
                error_msg = result.error_message or "Video generation failed"
                logger.error(f"Video {video_id} failed: {error_msg}")
                raise PixverseAPIError(error_msg)
            elif result.status == VideoStatus.CANCELLED:
                logger.warning(f"Video {video_id} was cancelled")
                raise PixverseAPIError("Video generation was cancelled")
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= max_wait_time:
                logger.error(f"Video {video_id} timed out after {elapsed:.1f}s")
                raise PixverseTimeoutError(f"Video generation timed out after {max_wait_time}s")
            
            logger.debug(f"Video {video_id} status: {result.status}, waiting {poll_interval}s...")
            await asyncio.sleep(poll_interval)

    async def upload_and_generate_video(
        self,
        image_path: str,
        prompt: str,
        model: str = "v5",
        duration: int = 5,
        quality: str = "540p",
        wait_for_completion: bool = True,
        max_wait_time: int = 300,
        **kwargs
    ) -> VideoGenerationResponse:
        """
        Complete workflow: upload image and generate video with auto-polling.

        Args:
            image_path: Path to the image file
            prompt: Text prompt for video generation
            model: Model version (default: v5)
            duration: Video duration (default: 5)
            quality: Video quality (default: 540p)
            wait_for_completion: Whether to wait for completion (default: True)
            max_wait_time: Maximum wait time in seconds (default: 300)
            **kwargs: Additional parameters for video generation

        Returns:
            Final video generation response (if wait_for_completion=True)
            or initial response with video_id (if wait_for_completion=False)
        """
        logger.info(f"Starting complete workflow: {image_path} -> video")
        
        # Step 1: Upload image
        logger.info("Step 1: Uploading image...")
        upload_result = await self.upload_image(image_path)
        logger.info(f"Image uploaded successfully, img_id: {upload_result.img_id}")
        
        # Step 2: Generate video
        logger.info("Step 2: Generating video...")
        request = ImageToVideoRequest(
            img_id=upload_result.img_id,
            prompt=prompt,
            model=model,
            duration=duration,
            quality=quality,
            **kwargs
        )
        
        video_response = await self.image_to_video(request)
        logger.info(f"Video generation started, video_id: {video_response.video_id}")
        
        # Step 3: Wait for completion (optional)
        if wait_for_completion:
            logger.info("Step 3: Waiting for video completion...")
            final_result = await self.wait_for_video_completion(
                video_response.video_id,
                max_wait_time=max_wait_time
            )
            logger.info("Complete workflow finished successfully!")
            return final_result
        else:
            return video_response
