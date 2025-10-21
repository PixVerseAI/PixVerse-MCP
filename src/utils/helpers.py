"""
Helper utilities for Pixverse MCP.
"""

import uuid
from typing import Any, Dict, Optional


def generate_trace_id() -> str:
    """Generate a unique trace ID for request tracking."""
    return str(uuid.uuid4())


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error message with context.

    Args:
        error: Exception object
        context: Optional context information

    Returns:
        Formatted error message
    """
    base_message = str(error)

    if context:
        return f"{context}: {base_message}"

    return base_message


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize prompt text for API submission.

    Args:
        prompt: Raw prompt text

    Returns:
        Sanitized prompt text
    """
    # Remove excessive whitespace
    prompt = " ".join(prompt.split())

    # Trim to maximum length
    if len(prompt) > 2048:
        prompt = prompt[:2045] + "..."

    return prompt


def build_request_summary(request_type: str, params: Dict[str, Any]) -> str:
    """
    Build a summary string for a request.

    Args:
        request_type: Type of request
        params: Request parameters

    Returns:
        Summary string
    """
    summary_parts = [f"Type: {request_type}"]

    # Add key parameters to summary
    if "prompt" in params:
        prompt = params["prompt"][:50] + "..." if len(params["prompt"]) > 50 else params["prompt"]
        summary_parts.append(f"Prompt: {prompt}")

    if "model" in params:
        summary_parts.append(f"Model: {params['model']}")

    if "duration" in params:
        summary_parts.append(f"Duration: {params['duration']}s")

    if "quality" in params:
        summary_parts.append(f"Quality: {params['quality']}")

    if "img_id" in params:
        summary_parts.append(f"Image ID: {params['img_id']}")

    if "template_id" in params and params["template_id"]:
        summary_parts.append(f"Template: {params['template_id']}")

    return " | ".join(summary_parts)


def extract_video_id_from_response(response_data: Dict[str, Any]) -> Optional[int]:
    """
    Extract video ID from API response.

    Args:
        response_data: API response data

    Returns:
        Video ID if found, None otherwise
    """
    # Try different possible locations for video_id
    resp_data = response_data.get("Resp", {})

    if isinstance(resp_data, dict):
        return resp_data.get("video_id")

    # Fallback to top-level
    return response_data.get("video_id")


def get_popular_templates() -> Dict[int, str]:
    """
    Get mapping of popular template IDs to names.

    Returns:
        Dictionary mapping template ID to name
    """
    return {
        315446315336768: "Kiss Kiss",
        315447659476032: "Kungfu Club",
        315447659476033: "Earth Zoom",
        316826014376384: "General Effects",
        313555098280384: "App Filter Template",
        321958627120000: "App Filter Template 2",
    }


def get_recommended_settings(model: str) -> Dict[str, Any]:
    """
    Get recommended settings for a model.

    Args:
        model: Model version

    Returns:
        Dictionary of recommended settings
    """
    if model == "v5":
        return {
            "duration": 5,
            "quality": "540p",
            "motion_mode": "normal",
            "sound_effect_switch": True,
        }
    elif model in ["v4", "v4.5"]:
        return {
            "duration": 5,
            "quality": "540p",
            "motion_mode": "normal",
        }
    else:
        return {
            "duration": 5,
            "quality": "540p",
        }
