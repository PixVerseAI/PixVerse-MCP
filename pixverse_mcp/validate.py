"""Validation utilities for PixVerse API parameters."""

from typing import Union

# Validate aspect ratio
def validate_aspect_ratio(aspect_ratio: str) -> str:
    """Validate if aspect ratio is supported"""
    supported_ratios = ["16:9", "4:3", "1:1", "3:4", "9:16"]
    if aspect_ratio not in supported_ratios:
        raise ValueError(f"Unsupported aspect ratio. Supported values: {', '.join(supported_ratios)}")
    return aspect_ratio

# Validate duration
def validate_duration(duration: int, quality: str) -> int:
    """Validate duration based on quality"""
    if duration not in [5, 8]:
        raise ValueError("Duration must be 5 or 8 seconds")

    if quality == "1080p" and duration == 8:
        raise ValueError("1080p quality does not support 8-second duration")

    return duration

# Validate quality
def validate_quality(quality: str) -> str:
    """Validate if video quality is supported"""
    supported_qualities = ["360p","540p", "720p", "1080p"]
    if quality not in supported_qualities:
        raise ValueError(f"Unsupported quality. Supported values: {', '.join(supported_qualities)}")
    return quality

# Validate motion mode
def validate_motion_mode(motion_mode: str) -> str:
    """Validate if motion mode is supported"""
    supported_modes = ["normal", "fast"]
    if motion_mode not in supported_modes:
        raise ValueError(f"Unsupported motion mode. Supported values: {', '.join(supported_modes)}")
    return motion_mode

# Validate model
def validate_model(model: str) -> str:
    """Validate if model version is supported"""
    supported_models = ["v3.5"]
    if model not in supported_models:
        raise ValueError(f"Unsupported model. Supported values: {', '.join(supported_models)}")
    return model

# Validate seed
def validate_seed(seed: int) -> int:
    """Validate if seed is within range"""
    if not (0 <= seed <= 2147483647):
        raise ValueError("Seed must be between 0 and 2147483647")
    return seed