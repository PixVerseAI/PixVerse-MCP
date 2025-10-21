"""
Validation utilities for Pixverse API requests.
"""

from typing import Any, Dict, List, Optional

from ..exceptions import PixverseValidationError
from ..models.common import ModelVersion, MotionMode, VideoQuality


def validate_model_constraints(
    model: str,
    quality: str,
    duration: int,
    motion_mode: Optional[str] = None,
) -> None:
    """
    Validate model-specific constraints.

    Args:
        model: Model version
        quality: Video quality
        duration: Video duration
        motion_mode: Motion mode

    Raises:
        PixverseValidationError: If constraints are violated
    """
    # V5 model constraints
    if model == ModelVersion.V5:
        if motion_mode == MotionMode.FAST:
            raise PixverseValidationError("V5 model does not support fast motion mode", field="motion_mode")

    # Quality constraints
    if quality == VideoQuality.Q1080P and duration > 5:
        raise PixverseValidationError("1080p quality does not support duration > 5 seconds", field="quality")

    # Motion mode constraints
    if motion_mode == MotionMode.FAST and duration > 5:
        raise PixverseValidationError("Fast motion mode only supports duration <= 5 seconds", field="motion_mode")


def validate_request_params(params: Dict[str, Any]) -> List[str]:
    """
    Validate request parameters and return list of warnings.

    Args:
        params: Request parameters

    Returns:
        List of validation warnings
    """
    warnings = []

    # Check for conflicting parameters
    if params.get("template_id") and params.get("camera_movement"):
        warnings.append("template_id and camera_movement cannot be used together")

    if params.get("img_id") and params.get("img_ids"):
        warnings.append("img_id and img_ids cannot be used together")

    if params.get("sound_effect_content") and params.get("sound_mode"):
        warnings.append("sound_effect_content and sound_mode cannot be used together")

    if params.get("source_video_id") and params.get("video_media_id"):
        warnings.append("source_video_id and video_media_id cannot be used together")

    # Check required parameters for specific scenarios
    template_id = params.get("template_id", 0)
    if template_id == 0:  # Non-template scenario
        if not params.get("img_id") and not params.get("img_ids"):
            warnings.append("img_id or img_ids required when template_id is not provided")

    return warnings


def validate_fusion_prompt(prompt: str, image_references: List[Dict[str, Any]]) -> None:
    """
    Validate fusion prompt contains all required references.

    Args:
        prompt: Prompt text
        image_references: List of image references

    Raises:
        PixverseValidationError: If validation fails
    """
    ref_names = {ref["ref_name"] for ref in image_references}

    for ref_name in ref_names:
        if f"@{ref_name}" not in prompt:
            raise PixverseValidationError(f"Reference @{ref_name} not found in prompt", field="prompt")

    # Check for unique ref_names
    all_ref_names = [ref["ref_name"] for ref in image_references]
    if len(all_ref_names) != len(set(all_ref_names)):
        raise PixverseValidationError("All ref_names must be unique", field="image_references")
