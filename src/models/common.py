"""
Common enums and types used across Pixverse API models.
"""

from enum import Enum
from typing import Literal


class ModelVersion(str, Enum):
    """Supported model versions."""

    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    V3_5 = "v3.5"
    V4 = "v4"
    V4_5 = "v4.5"
    V5 = "v5"
    VISIONARY = "visionary"


class VideoQuality(str, Enum):
    """Video quality options."""

    Q360P = "360p"
    Q540P = "540p"
    Q720P = "720p"
    Q1080P = "1080p"


class MotionMode(str, Enum):
    """Motion mode options."""

    NORMAL = "normal"
    FAST = "fast"


class CameraMovement(str, Enum):
    """Camera movement options."""

    HORIZONTAL_RIGHT = "horizontal_right"
    HORIZONTAL_LEFT = "horizontal_left"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    VERTICAL_UP = "vertical_up"
    VERTICAL_DOWN = "vertical_down"
    CRANE_UP = "crane_up"
    QUICKLY_ZOOM_IN = "quickly_zoom_in"
    QUICKLY_ZOOM_OUT = "quickly_zoom_out"
    SMOOTH_ZOOM_IN = "smooth_zoom_in"
    CAMERA_ROTATION = "camera_rotation"
    ROBO_ARM = "robo_arm"
    SUPER_DOLLY_OUT = "super_dolly_out"
    WHIP_PAN = "whip_pan"
    HITCHCOCK = "hitchcock"
    LEFT_FOLLOW = "left_follow"
    RIGHT_FOLLOW = "right_follow"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    FIX_BG = "fix_bg"
    DEFAULT = "default"


class VideoStyle(str, Enum):
    """Video style options."""

    ANIME = "anime"
    ANIMATION_3D = "3d_animation"
    CLAY = "clay"
    REALISTIC = "realistic"
    COMIC = "comic"
    CYBERPUNK = "cyberpunk"


class AspectRatio(str, Enum):
    """Aspect ratio options."""

    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"
    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_9_16 = "9:16"


class SoundMode(str, Enum):
    """Sound effect mode options."""

    DEFAULT_MUSIC = "default_music"


class FusionType(str, Enum):
    """Fusion image reference types."""

    SUBJECT = "subject"
    BACKGROUND = "background"


# Type aliases for better readability
Duration = Literal[5, 8, 10]
Seed = int
TemplateId = int
ImageId = int
VideoId = int
