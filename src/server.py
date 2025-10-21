"""
MCP server implementation for Pixverse video generation.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Sequence

from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
    ContentBlock,
)
from pydantic import ValidationError

from .client import PixverseClient
from .exceptions import PixverseError
from .config import get_config, PixverseConfig
from .models.requests import (
    ExtendVideoRequest,
    FusionVideoRequest,
    ImageToVideoRequest,
    LipSyncVideoRequest,
    SoundEffectVideoRequest,
    TextToVideoRequest,
    TransitionVideoRequest,
)


class PixverseMCPServer:
    """MCP Server for Pixverse video generation APIs."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Optional[PixverseConfig] = None
        self.server = Server("pixverse-mcp")
        self.client: Optional[PixverseClient] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="capabilities_overview",
                    description="""System Capabilities Overview - Read before planning video production workflow.

CORE CONSTRAINTS:
• Single generation: Maximum 5s or 8s per call
• For videos >8s: Must chain multiple generations using extend_video or compose multiple segments
• Status checking: Poll get_video_status every 6 seconds until completion
• Generation time: Typically 60-120 seconds per segment
• Concurrency limits: Each account has its own concurrent generation limit
  - Multiple independent videos CAN be generated in parallel (e.g., different calls)
  - Test your account's concurrent capacity to optimize throughput

AVAILABLE CAPABILITIES:

1. TEXT → VIDEO (text_to_video)
   - Generate video from text description alone
   - No reference images needed
   - Full creative control through prompts
   - Supports styles, camera movements, sound effects

2. IMAGE → VIDEO (image_to_video)
   - Animate static images
   - Requires upload_image first to get img_id
   - Better visual consistency with reference
   - Supports single or multiple images with templates

3. VIDEO EXTENSION (extend_video)
   - Continue existing video seamlessly
   - Key tool for creating longer sequences
   - Maintains visual continuity from source
   - Can be chained infinitely for any length

4. SCENE TRANSITIONS (transition_video)
   - Smooth morphing between two images
   - Requires two img_ids (first_frame, last_frame)
   - Creates bridging animation
   - Perfect for multi-scene storytelling

5. LIP SYNC (lip_sync_video)
   - Add realistic lip sync to talking head videos
   - Supports uploaded audio or TTS (text-to-speech)
   - Automatically matches mouth movements to audio
   - Multiple speaker voices available via get_tts_speakers

6. SOUND EFFECTS (sound_effect_video)
   - Add AI-generated sound effects to any video
   - Contextual sounds based on text description
   - Can preserve or replace original audio
   - Ambient sounds, foley effects, music, etc.

7. FUSION VIDEO (fusion_video)
   - Composite multiple subjects into one scene (v4.5 only)
   - Reference subjects using @ref_name syntax
   - Combine 1-3 image references (subjects/backgrounds)
   - Create impossible combinations naturally

8. RESOURCE UPLOADS (upload_image, upload_video)
   - Upload local files or from URLs
   - Images: jpg, jpeg, png, webp
   - Videos: mp4, mov
   - Returns resource IDs for other operations

9. TTS SPEAKERS (get_tts_speakers)
   - List available text-to-speech voice options
   - Get speaker_id for use in lip_sync_video
   - Multiple languages and accents
   - Pagination support for browsing voices

10. STATUS CHECK (get_video_status)
    - Monitor video generation progress
    - Retrieve completed video URL
    - Check for errors or failures
    - Poll every 6 seconds until ready

WHAT YOU CAN BUILD:
• Single-scene videos (5-8s): Direct generation
• Extended sequences (any length): Chain segments with extend_video
• Multi-scene stories: Combine different generations with or without transitions
• Image animations: Upload + animate + extend
• Hybrid content: Mix text-gen and image-gen segments
• Smooth narratives: Use transitions between scene changes
• Talking character videos: Generate/upload video + lip sync with audio/TTS
• Enhanced videos: Add sound effects, ambient sounds, music
• Composite scenes: Fusion video with multiple subjects and backgrounds

SYSTEM BEHAVIOR:
• Polling required: Videos don't generate instantly, must check status
• Async nature: Submit job → get video_id → poll until ready
• Modular design: Each tool does one thing, combine them for complex results
• Resource management: Upload assets first, then reference by ID
• Parallel generation: Submit multiple independent videos simultaneously to maximize throughput
  - Good: Generate 3 different text_to_video scenes at once
  - Bad: Try to extend_video before previous segment completes
  - Strategy: For multi-scene projects, generate all initial scenes in parallel, then extend each

Your task: Analyze user requirements, understand constraints, and design an appropriate workflow using these capabilities.""",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "description": "Informational overview, not a callable tool"
                    },
                ),
                Tool(
                    name="text_to_video",
                    description="""Generate video from text prompt.

CAPABILITIES:
• Creates video from text description alone
• Supports various styles (anime, 3d_animation, clay, comic, cyberpunk)
• Camera movement controls available (zoom, pan, rotation, etc.) - v4/v4.5 only
• Duration: 5s or 8s per generation
• Quality: 360p to 1080p

WHEN TO USE:
• No reference images available
• Abstract concepts or imagined scenes
• Starting point for longer sequences (combine with extend_video)
• Creative scenarios requiring full prompt control

LIMITATIONS:
• Cannot exceed 8s in single call
• For longer videos: chain with extend_video or create separate segments""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation (max 2048 chars)",
                                "maxLength": 2048,
                            },
                            "model": {
                                "type": "string",
                                "enum": ["v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version to use",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16"],
                                "default": "16:9",
                                "description": "Video aspect ratio",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                            "style": {
                                "type": "string",
                                "enum": ["anime", "3d_animation", "clay", "comic", "cyberpunk"],
                                "description": "Video style (optional)",
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "Negative prompt (optional)",
                                "maxLength": 2048,
                            },
                            "motion_mode": {
                                "type": "string",
                                "enum": ["normal", "fast"],
                                "default": "normal",
                                "description": "Motion mode",
                            },
                            "camera_movement": {
                                "type": "string",
                                "enum": [
                                    "horizontal_right",
                                    "horizontal_left",
                                    "zoom_in",
                                    "zoom_out",
                                    "vertical_up",
                                    "vertical_down",
                                    "crane_up",
                                    "quickly_zoom_in",
                                    "quickly_zoom_out",
                                    "smooth_zoom_in",
                                    "camera_rotation",
                                    "robo_arm",
                                    "super_dolly_out",
                                    "whip_pan",
                                    "hitchcock",
                                    "left_follow",
                                    "right_follow",
                                    "pan_left",
                                    "pan_right",
                                    "fix_bg",
                                    "default",
                                ],
                                "description": "Camera movement (optional, cannot use with template_id)",
                            },
                            "template_id": {
                                "type": "integer",
                                "description": "Template ID (optional, cannot use with camera_movement)",
                            },
                            "seed": {"type": "integer", "description": "Random seed (optional)"},
                            "sound_effect_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Enable sound effects",
                            },
                            "sound_effect_content": {
                                "type": "string",
                                "description": "Sound effect description (optional)",
                                "maxLength": 2048,
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="image_to_video",
                    description="""Animate static images into video.

CAPABILITIES:
• Brings still images to life with motion
• Better visual consistency than text_to_video (uses image as reference)
• Supports single image or multiple images (with templates)
• Duration: 5s or 8s per generation
• Prompt guides animation style and motion

REQUIREMENTS:
• Must call upload_image first to obtain img_id
• img_id required as input parameter

WHEN TO USE:
• Have photos, artwork, or visual references
• Want consistent visual style based on reference
• Creating photo animations or slideshow-style videos
• Need visual control beyond text descriptions

EXTENSIBILITY:
• Can extend with extend_video for longer sequences
• Can connect multiple images with transition_video""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation (max 2048 chars)",
                                "maxLength": 2048,
                            },
                            "img_id": {"type": "integer", "description": "Image ID for single image"},
                            "img_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Array of image IDs for multiple images only supports with multi-templates",
                            },
                            "model": {
                                "type": "string",
                                "enum": ["v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version to use",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                            "style": {
                                "type": "string",
                                "enum": ["anime", "3d_animation", "clay", "comic", "cyberpunk"],
                                "description": "Video style (optional)",
                            },
                            "template_id": {"type": "integer", "description": "Template ID (optional)ß"},
                            "motion_mode": {
                                "type": "string",
                                "enum": ["normal", "fast"],
                                "default": "normal",
                                "description": "Motion mode",
                            },
                            "sound_effect_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Enable sound effects",
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="transition_video",
                    description="""Create smooth transition between two images.

CAPABILITIES:
• Generates morphing animation from first image to last image
• Creates visual continuity between different scenes
• Duration: 5s or 8s
• Prompt guides transition style

REQUIREMENTS:
• Two img_ids needed: first_frame_img and last_frame_img
• Both images must be uploaded via upload_image first

WHEN TO USE:
• Connecting different scenes or compositions
• Multi-scene narratives requiring smooth visual flow
• Photo montages with elegant transitions
• Scene changes where visual continuity matters

CREATIVE POTENTIAL:
• Day-to-night transitions
• Character transformations
• Location changes
• Abstract visual morphing""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation",
                                "maxLength": 2048,
                            },
                            "first_frame_img": {"type": "integer", "description": "First frame image ID"},
                            "last_frame_img": {"type": "integer", "description": "Last frame image ID"},
                            "model": {
                                "type": "string",
                                "enum": ["v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version to use",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                        },
                        "required": ["prompt", "first_frame_img", "last_frame_img"],
                    },
                ),
                Tool(
                    name="extend_video",
                    description="""Continue an existing video with additional footage.

CAPABILITIES:
• Extends any generated video by 5s or 8s
• Maintains visual continuity from source video
• Can be chained multiple times for arbitrary length
• Prompt can remain consistent or evolve for story progression

REQUIREMENTS:
• source_video_id from a previously generated video

WHEN TO USE:
• Any video requirement exceeding 8s duration
• Creating longer narratives or sequences
• Continuing visual story from initial generation

KEY INSIGHT:
This is the primary method for creating videos longer than the 8s single-generation limit. Any multi-second video requirement will likely need this tool.

FLEXIBILITY:
• Keep same prompt = smooth continuation
• Evolve prompt = gradual scene progression
• No strict limit on chain length (though quality may degrade after many extensions)""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video extension",
                                "maxLength": 2048,
                            },
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "model": {
                                "type": "string",
                                "enum": ["v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="lip_sync_video",
                    description="""Generate lip sync video with synchronized mouth movements.

CAPABILITIES:
• Adds realistic lip sync to talking head videos
• Supports both uploaded audio and TTS (text-to-speech)
• Automatically matches mouth movements to audio timing
• Works with both generated videos and uploaded videos

INPUT OPTIONS:
• Audio: Upload audio file (audio_media_id) OR use TTS (lip_sync_tts_content + speaker_id)
• Video: Generated video (source_video_id) OR uploaded video (video_media_id)

WHEN TO USE:
• Creating talking character videos
• Adding voiceovers to portrait videos
• Dubbing existing videos with new dialogue
• Character animations with speech

TTS FEATURES:
• Multiple speaker voices available (use get_tts_speakers to list)
• Text limit: 200 characters per generation
• Supports various languages and accents

WORKFLOW:
• With custom audio: upload_video + upload_audio → lip_sync_video
• With TTS: generate/upload video + choose speaker → lip_sync_video with text""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "audio_media_id": {"type": "integer", "description": "Audio media ID (uploaded audio)"},
                            "lip_sync_tts_speaker_id": {"type": "string", "description": "TTS speaker ID"},
                            "lip_sync_tts_content": {
                                "type": "string",
                                "description": "TTS content (max 200 chars)",
                                "maxLength": 200,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="sound_effect_video",
                    description="""Add AI-generated sound effects to video.

CAPABILITIES:
• Generates contextual sound effects based on text description
• Can preserve or replace original video audio
• AI analyzes video content and matches sound effects to visuals
• Duration matches source video length

INPUT:
• Video: Generated video (source_video_id) OR uploaded video (video_media_id)
• Description: Text describing desired sound effects (sound_effect_content)

WHEN TO USE:
• Adding ambient sounds (ocean waves, wind, rain, city noise)
• Creating foley effects (footsteps, door creaks, object interactions)
• Enhancing atmosphere (dramatic music, tension sounds)
• Replacing/augmenting existing audio

AUDIO CONTROL:
• original_sound_switch=true: Mixes new effects with existing audio
• original_sound_switch=false: Replaces audio entirely with new effects

CREATIVE EXAMPLES:
• Nature videos: "Gentle ocean waves, seagull calls, soft wind"
• Urban scenes: "Busy city traffic, people chatting, car horns"
• Dramatic moments: "Suspenseful music, thunder rumbling"
• Fantasy: "Magical sparkles, mystical ambiance, ethereal tones\"""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sound_effect_content": {
                                "type": "string",
                                "description": "Sound effect description",
                                "maxLength": 2048,
                            },
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "original_sound_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Keep original sound",
                            },
                        },
                        "required": ["sound_effect_content"],
                    },
                ),
                Tool(
                    name="fusion_video",
                    description="""Generate fusion video compositing multiple subjects into one scene (v4.5 only).

CAPABILITIES:
• Combines multiple subjects/backgrounds into a single coherent video
• Reference subjects by name in prompt using @ref_name syntax
• Supports 1-3 image references per video
• Each reference can be a subject or background
• AI composites them naturally into unified scene

HOW IT WORKS:
1. Upload reference images (subjects/backgrounds)
2. Assign each a ref_name (e.g., "person", "cat", "beach")
3. In prompt, reference them: "@person walking on the @beach with a @cat"
4. AI generates video with all elements composed together

REFERENCE TYPES:
• subject: Main elements (characters, objects, specific items)
• background: Environmental settings (locations, scenery)

WHEN TO USE:
• Placing specific characters in custom environments
• Creating impossible combinations (person + fantasy background)
• Product placement in various contexts
• Character interactions that don't exist in reality

LIMITATIONS:
• v4.5 model only (not available in v5)
• Maximum 3 image references per video
• ref_name must be alphanumeric, max 30 characters

EXAMPLE WORKFLOW:
1. upload_image(portrait.jpg) → img_id_1 (ref_name="hero", type="subject")
2. upload_image(castle.jpg) → img_id_2 (ref_name="castle", type="background")
3. fusion_video(prompt="@hero standing in front of @castle at sunset")
Result: Portrait character composited into castle scene""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt with @ref_name references",
                                "maxLength": 2048,
                            },
                            "image_references": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["subject", "background"]},
                                        "img_id": {"type": "integer"},
                                        "ref_name": {"type": "string", "maxLength": 30},
                                    },
                                    "required": ["type", "img_id", "ref_name"],
                                },
                                "minItems": 1,
                                "maxItems": 3,
                            },
                            "duration": {"type": "integer", "enum": [5, 8], "default": 5},
                            "quality": {"type": "string", "enum": ["360p", "540p", "720p", "1080p"], "default": "540p"},
                            "aspect_ratio": {
                                "type": "string",
                                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16"],
                                "default": "16:9",
                            },
                        },
                        "required": ["prompt", "image_references"],
                    },
                ),
                                Tool(
                    name="upload_image",
                    description="""Upload image file or from URL to Pixverse for video generation.

CAPABILITIES:
• Upload local image files from disk
• Upload images directly from URLs
• Supports: jpg, jpeg, png, webp formats
• Returns img_id for use in other tools

WHEN TO USE:
• Before calling image_to_video (requires img_id)
• Before calling transition_video (requires 2 img_ids)
• Before calling fusion_video (requires 1-3 img_ids)

INPUT OPTIONS:
• file_path: Path to local image file
• image_url: Direct URL to image
(Provide ONE, not both)

WORKFLOW:
1. upload_image → receive img_id in response
2. Use img_id in generation tools (image_to_video, transition_video, fusion_video)

RETURNS:
• img_id: Integer identifier for the uploaded image
• img_url: Pixverse CDN URL where image is stored
• File metadata (name, size, type)""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the local image file to upload (supports jpg, jpeg, png, webp formats)",
                            },
                            "image_url": {
                                "type": "string",
                                "description": "URL of the image to upload (alternative to file_path)",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="upload_video",
                    description="""Upload video file or from URL to Pixverse for video extension or other operations.

CAPABILITIES:
• Upload local video files from disk
• Upload videos directly from URLs
• Supports: mp4, mov formats
• Returns video_media_id for use in other tools

WHEN TO USE:
• Before calling extend_video on existing footage (needs video_media_id)
• Before calling lip_sync_video on external videos
• Before calling sound_effect_video on external videos
• When you want to extend/modify videos not generated by this system

INPUT OPTIONS:
• file_path: Path to local video file
• file_url: Direct URL to video
(Provide ONE, not both)

WORKFLOW:
1. upload_video → receive video_media_id in response
2. Use video_media_id in processing tools (extend_video, lip_sync_video, sound_effect_video)

RETURNS:
• video_media_id: Integer identifier for the uploaded video
• media_url: Pixverse CDN URL where video is stored
• File metadata (name, size, type, duration)

NOTE: For videos generated by this system, use source_video_id directly (no upload needed)""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the local video file to upload (supports mp4, mov, avi formats)",
                            },
                            "file_url": {
                                "type": "string",
                                "description": "URL of the video file to upload (alternative to file_path)",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="get_tts_speakers",
                    description="""Get list of available TTS speakers for lip sync.

CAPABILITIES:
• Lists all available text-to-speech voice options
• Provides speaker_id needed for lip_sync_video
• Shows speaker names and characteristics
• Supports pagination for large speaker lists

WHEN TO USE:
• Before using lip_sync_video with TTS
• When user wants to choose specific voice character
• To discover available voice options

PARAMETERS:
• page_num: Page number (default: 1)
• page_size: Results per page (default: 30)

RETURNS:
• List of speakers with:
  - speaker_id: Unique identifier to use in lip_sync_video
  - name: Speaker name/description
  - Additional metadata (language, accent, gender, etc.)

WORKFLOW:
1. get_tts_speakers() → browse available voices
2. Choose speaker_id
3. Use in lip_sync_video(lip_sync_tts_speaker_id=..., lip_sync_tts_content="text")""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_num": {"type": "integer", "default": 1, "description": "Page number"},
                            "page_size": {"type": "integer", "default": 30, "description": "Page size"},
                        },
                    },
                ),
                Tool(
                    name="get_video_status",
                    description="""Get video generation status and result by video ID.

CAPABILITIES:
• Check real-time generation progress
• Retrieve completed video URL
• Monitor for failures or errors
• Get video metadata (resolution, size, seed, etc.)

STATUS VALUES:
• pending: Video queued, generation not started
• in_progress: Actively generating
• completed: Ready! video_url available
• failed: Generation failed, error_message provided

POLLING BEHAVIOR:
• IMPORTANT: Wait 6 seconds between each status check
• Typical generation time: 60-120 seconds per segment
• Don't poll too frequently (wastes resources, doesn't speed up generation)

WHEN TO USE:
• After calling any video generation tool (text_to_video, image_to_video, etc.)
• Every 6 seconds until status becomes "completed" or "failed"
• To retrieve final video URL after completion

RETURNS:
• status: Current generation state
• video_url: Download URL (when completed)
• resolution: Video dimensions (when completed)
• file_size: Video file size
• seed: Random seed used
• error_message: Failure reason (if failed)

WORKFLOW:
1. Call generation tool → receive video_id
2. Wait 6 seconds
3. get_video_status(video_id)
4. If pending/in_progress: repeat step 2-3
5. If completed: use video_url
6. If failed: check error_message""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_id": {
                                "type": "integer",
                                "description": "Video ID to check status for",
                            },
                        },
                        "required": ["video_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Handle tool calls - Cursor compatible version."""
            try:
                if not self.client:
                    raise PixverseError("Pixverse client not initialized")

                # Check if this is a video generation tool that should include polling
                video_generation_tools = [
                    "text_to_video", "image_to_video", "transition_video", 
                    "extend_video", "lip_sync_video", "sound_effect_video", "fusion_video"
                ]
                
                if name in video_generation_tools:
                    # Handle video generation with automatic polling
                    if name == "text_to_video":
                        request = TextToVideoRequest(**arguments)
                    elif name == "image_to_video":
                        request = ImageToVideoRequest(**arguments)
                    elif name == "transition_video":
                        request = TransitionVideoRequest(**arguments)
                    elif name == "extend_video":
                        request = ExtendVideoRequest(**arguments)
                    elif name == "lip_sync_video":
                        request = LipSyncVideoRequest(**arguments)
                    elif name == "sound_effect_video":
                        request = SoundEffectVideoRequest(**arguments)
                    elif name == "fusion_video":
                        request = FusionVideoRequest(**arguments)
                    else:
                        raise PixverseError(f"Unsupported video generation tool: {name}")
                    
                    # 分步骤流程：快速提交任务，返回video_id供后续查询
                    if name == "text_to_video":
                        result = await self.client.text_to_video(request)
                    elif name == "image_to_video":
                        result = await self.client.image_to_video(request)
                    elif name == "transition_video":
                        result = await self.client.transition_video(request)
                    elif name == "extend_video":
                        result = await self.client.extend_video(request)
                    elif name == "lip_sync_video":
                        result = await self.client.lip_sync_video(request)
                    elif name == "sound_effect_video":
                        result = await self.client.sound_effect_video(request)
                    elif name == "fusion_video":
                        result = await self.client.fusion_video(request)
                    
                    # 返回提交成功的信息，指导LLM进行自动轮询
                    return {
                        "success": True,
                        "message": f"{name} has been successfully submitted",
                        "video_id": result.video_id,
                        "status": "submitted",
                        "next_step": "Call the get_video_status endpoint every 6 seconds to check the generation status, up to 2 minutes (20 attempts).",
                        "polling_config": {
                            "interval_seconds": 6,
                            "timeout_minutes": 2,
                            "max_attempts": 20
                        },
                        "estimated_time": "Estimated completion time: 1–2 minutes.",
                        "instruction_for_llm": "Start polling immediately. Call get_video_status every 6 seconds until the status becomes 'completed' or the request times out."
                    }
                
                elif name == "upload_image":
                    # Handle image upload (file or URL)
                    file_path = arguments.get("file_path")
                    image_url = arguments.get("image_url")
                    
                    if not file_path and not image_url:
                        raise PixverseError("Either file_path or image_url is required")
                    
                    if file_path and image_url:
                        raise PixverseError("Only one of file_path or image_url should be provided")
                    
                    if file_path:
                        # Local file upload
                        from pathlib import Path
                        if not Path(file_path).exists():
                            raise PixverseError(f"Image file not found: {file_path}")
                        
                        # Check file format
                        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext not in allowed_extensions:
                            raise PixverseError(f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}")
                        
                        # Upload image file
                        result = await self.client.upload_image(file_path=file_path)
                        
                        return {
                            "success": True,
                            "message": "Image file uploaded successfully",
                            "img_id": result.img_id,
                            "img_url": result.img_url,
                            "file_path": file_path,
                            "file_name": Path(file_path).name,
                            "upload_type": "file",
                            "next_step": "You can now use img_id to call the image_to_video endpoint to generate a video."
                        }
                    else:
                        # URL upload
                        import re
                        # Basic URL validation
                        url_pattern = re.compile(
                            r'^https?://'  # http:// or https://
                            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                            r'localhost|'  # localhost...
                            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                            r'(?::\d+)?'  # optional port
                            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                        
                        if not url_pattern.match(image_url):
                            raise PixverseError(f"Invalid image URL format: {image_url}")
                        
                        # Upload image from URL
                        result = await self.client.upload_image(image_url=image_url)
                        
                        return {
                            "success": True,
                            "message": "Image file uploaded successfully",
                            "img_id": result.img_id,
                            "img_url": result.img_url,
                            "source_url": image_url,
                            "upload_type": "url",
                            "next_step": "You can now use img_id to call the image_to_video endpoint to generate a video."
                        }
                
                elif name == "upload_video":
                    # Handle video upload (file or URL)
                    file_path = arguments.get("file_path")
                    file_url = arguments.get("file_url")
                    
                    if not file_path and not file_url:
                        raise PixverseError("Either file_path or file_url is required")
                    
                    if file_path and file_url:
                        raise PixverseError("Only one of file_path or file_url should be provided")
                    
                    if file_path:
                        # Local file upload
                        from pathlib import Path
                        if not Path(file_path).exists():
                            raise PixverseError(f"Video file not found: {file_path}")
                        
                        # Check file format
                        allowed_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext not in allowed_extensions:
                            raise PixverseError(f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}")
                        
                        # Upload video file
                        result = await self.client.upload_media(file_path=file_path, media_type="video")
                        
                        return {
                            "success": True,
                            "message": "Video URL uploaded successfully",
                            "video_media_id": result.media_id,
                            "media_url": result.url,
                            "media_type": result.media_type,
                            "file_path": file_path,
                            "file_name": Path(file_path).name,
                            "file_size": Path(file_path).stat().st_size,
                            "upload_type": "file",
                            "next_step": "Next, use video_media_id with the extend_video/lipsynnc/sound_effect/restyle endpoint"
                        }
                    else:
                        # URL upload
                        import re
                        # Basic URL validation
                        url_pattern = re.compile(
                            r'^https?://'  # http:// or https://
                            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                            r'localhost|'  # localhost...
                            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                            r'(?::\d+)?'  # optional port
                            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                        
                        if not url_pattern.match(file_url):
                            raise PixverseError(f"Invalid video URL format: {file_url}")
                        
                        # Upload video from URL
                        result = await self.client.upload_media(file_url=file_url, media_type="video")
                        
                        return {
                            "success": True,
                            "message": "Video URL uploaded successfully",
                            "video_media_id": result.media_id,
                            "media_url": result.url,
                            "media_type": result.media_type,
                            "source_url": file_url,
                            "upload_type": "url",
                            "next_step": "Next, use video_media_id with the extend_video/lipsynnc/sound_effect/restyle endpoint"
                        }

                elif name == "get_tts_speakers":
                    # Handle TTS speakers request
                    page_num = arguments.get("page_num", 1)
                    page_size = arguments.get("page_size", 30)
                    
                    result = await self.client.get_lip_sync_tts_list(page_num=page_num, page_size=page_size)
                    
                    # Format the result
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump()
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    else:
                        result_dict = result
                    
                    # 返回字典格式，避免Cursor客户端的字符串解析bug
                    speakers_data = result_dict.get('data', [])
                    total_speakers = result_dict.get('total', len(speakers_data))
                    
                    return {
                        "success": True,
                        "message": "TTS speaker list retrieved successfully",
                        "total_speakers": total_speakers,
                        "page": page_num,
                        "page_size": page_size,
                        "speakers": speakers_data,
                        "available_speakers": [
                            {
                                "speaker_id": speaker.get("speaker_id", ""),
                                "name": speaker.get("name", "")
                            } for speaker in speakers_data
                        ],
                        "next_step": "Use speaker_id to call the lip_sync_video endpoint for lip-sync generation"
                    }
                
                elif name == "get_video_status":
                    # Handle video status query
                    video_id = arguments.get("video_id")
                    if not video_id:
                        raise PixverseError("video_id is required")
                    
                    result = await self.client.get_video_result(video_id)
                    
                    # Format the result
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump()
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    else:
                        result_dict = result
                    
                    status_text = result.status.value if hasattr(result.status, 'value') else str(result.status)
                    
                    status_message = f"""get_video_status

🆔 Video_id: {video_id}
🔄 Status: {status_text}"""
                    
                    if result.status.value == "completed" if hasattr(result.status, 'value') else str(result.status) == "completed":
                        status_message += f"""
🎉 Video generated successfully!
🎬 Video_URL: {result.video_url if result.video_url else 'N/A'}"""
                        if result.outputWidth and result.outputHeight:
                            status_message += f"\n📏 Resolution: {result.outputWidth}x{result.outputHeight}"
                        if result.size:
                            status_message += f"\n📦 File size: {result.size} bytes"
                        if result.seed:
                            status_message += f"\n🎲 Seed: {result.seed}"
                    elif result.status.value == "failed" if hasattr(result.status, 'value') else str(result.status) == "failed":
                        error_msg = result.error_message if hasattr(result, 'error_message') and result.error_message else "未知错误"
                        status_message += f"""
❌ Video generation failed!
🚫 Error: {error_msg}"""
                    elif result.status.value in ["pending", "in_progress"] if hasattr(result.status, 'value') else str(result.status) in ["pending", "in_progress"]:
                        status_message += """
⏳ Video is being generated, please check again shortly"""
                    
                    # 返回结构化状态信息，包含预估时间和LLM指导
                    base_response = {
                        "success": True,
                        "video_id": video_id,
                        "status": status_text,
                        "message":"Video status retrieved successfully",
                        "video_url": result.video_url if hasattr(result, 'video_url') and result.video_url else None,
                        "resolution": f"{result.outputWidth}x{result.outputHeight}" if hasattr(result, 'outputWidth') and result.outputWidth else None,
                        "file_size": result.size if hasattr(result, 'size') and result.size else None,
                        "seed": result.seed if hasattr(result, 'seed') and result.seed else None,
                        "error_message": result.error_message if hasattr(result, 'error_message') and result.error_message else None,
                        "data": result_dict
                    }
                    
                    # 根据状态添加不同的指导信息
                    if status_text == "completed":
                        base_response.update({
                            "next_step": "Generation completed, you can stop polling",
                            "estimated_time": "Completed",
                            "instruction_for_llm": "The video has been generated. Please display the result to the user."
                        })
                    elif status_text == "failed":
                        base_response.update({
                            "next_step": "Generation failed, stop polling",
                            "estimated_time": "Failed",
                            "instruction_for_llm": "Video generation failed. Please inform the user of the error."
                        })
                    elif status_text in ["pending", "in_progress"]:
                        base_response.update({
                            "next_step": "Wait 6 seconds and check the status again",
                            "estimated_time": "Estimated 30–90 seconds remaining",
                            "instruction_for_llm": "The video is being generated. Please call get_video_status again after 6 seconds."
                        })
                    else:
                        base_response.update({
                            "next_step": "Wait 6 seconds and check the status again",
                            "estimated_time": "Unknown",
                            "instruction_for_llm": "Status is unknown. Please query again after 6 seconds."
                        })
                    
                    return base_response

                else:
                    raise PixverseError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error in handle_call_tool: {e}")
                # 返回结构化错误信息
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Fail to call the tool",
                    "tool_name": name
                }

    async def _generate_video_with_polling(self, tool_name: str, request_obj, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video and poll for completion status"""
        from .models.responses import VideoStatus
        
        # Submit generation request
        logger.info(f"🚀 {tool_name} task submitted...")
        if tool_name == "text_to_video":
            result = await self.client.text_to_video(request_obj)
        elif tool_name == "image_to_video":
            result = await self.client.image_to_video(request_obj)
        elif tool_name == "transition_video":
            result = await self.client.transition_video(request_obj)
        elif tool_name == "extend_video":
            result = await self.client.extend_video(request_obj)
        elif tool_name == "lip_sync_video":
            result = await self.client.lip_sync_video(request_obj)
        elif tool_name == "sound_effect_video":
            result = await self.client.sound_effect_video(request_obj)
        elif tool_name == "fusion_video":
            result = await self.client.fusion_video(request_obj)
        else:
            raise PixverseError(f"Unsupported tool for polling: {tool_name}")
        
        video_id = result.video_id
        logger.info(f"📹 Task submitted, Video ID:: {video_id}")
        
        # Start polling for status
        max_attempts = 20  # up to ~2 minute (20 * 6s)
        attempt = 0
        
        status_updates = [f"✅ {tool_name} task submitted"]
        status_updates.append(f"📹 Video ID: {video_id}")
        status_updates.append(f"🔄 Starting to check generation status...")
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                # Query status
                status_result = await self.client.get_video_result(video_id)
                status_text = status_result.status.value if hasattr(status_result.status, 'value') else str(status_result.status)
                
                status_updates.append(f"[{attempt:2d}/20] 状态: {status_text}")
                
                if status_result.status == VideoStatus.COMPLETED:
                    status_updates.append("🎉 Video generated successfully!")
                    if status_result.video_url:
                        status_updates.append(f"🎬 Video URL: {status_result.video_url}")
                    
                    # Return complete result with all details
                    return {
                        "success": True,
                        "status": "completed",
                        "message": "Video generation completed！",
                        "video_id": video_id,
                        "video_url": status_result.video_url,
                        "resolution": f"{status_result.outputWidth}x{status_result.outputHeight}" if hasattr(status_result, 'outputWidth') and status_result.outputWidth else None,
                        "file_size": getattr(status_result, 'size', None),
                        "seed": getattr(status_result, 'seed', None),
                        "style": getattr(status_result, 'style', None),
                        "polling_log": status_updates
                    }
                    
                elif status_result.status == VideoStatus.FAILED:
                    status_updates.append("\n❌ Video generation failed!")
                    error_msg = getattr(status_result, 'error_message', 'Unknown error')
                    if error_msg:
                        status_updates.append(f"Error message: {error_msg}")
                    
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "Video generation failed",
                        "video_id": video_id,
                        "error": error_msg,
                        "polling_log": status_updates
                    }
                    
                elif status_result.status in [VideoStatus.PENDING, VideoStatus.IN_PROGRESS]:
                    status_updates.append("    ⏳ Timeout reached. Please check the result later...")
                    await asyncio.sleep(3)  # wait 3 seconds
                else:
                    status_updates.append(f"    ❓ Unknown status: {status_result.status}")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"Error while querying status: {e}")
                status_updates.append(f"⚠️ Error querying status: {str(e)}")
                await asyncio.sleep(3)
        
        # Timeout
        status_updates.append(f"\n⏰ Timeout reached. Please check the result later")
        status_updates.append(f"📋 Video ID: {video_id}")
        
        return {
            "success": False,
            "status": "timeout",
            "message": "Timeout reached. Please check the result later.",
            "video_id": video_id,
            "polling_log": status_updates
        }

    async def initialize(self, config_path: Optional[str] = None):
        """Initialize the Pixverse client using configuration."""
        try:
            # Load configuration
            self.config = get_config(config_path or self.config_path)
            
            # Initialize client with config
            self.client = PixverseClient(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            
            logger.info(f"Pixverse MCP server initialized with config from: {config_path or self.config_path or 'environment'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pixverse MCP server: {e}")
            raise

    async def run(self):
        """Run the MCP server."""
        try:
            # Run the server with stdio streams
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="pixverse-mcp",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities=None,
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise


async def main(config_path: Optional[str] = None, mode: str = "stdio"):
    """Main entry point."""
    if mode == "sse":
        # Run SSE server
        logger.info("📡 Starting Pixverse MCP Server in SSE mode")
        try:
            from .sse_server import run_sse_server
            await run_sse_server(port=8080, config_path=config_path)
        except ImportError:
            logger.error("SSE server not available. Please install FastAPI dependencies.")
            raise
    else:
        # Run stdio server (default)
        logger.info("📡 Starting Pixverse MCP Server in STDIO mode")
        server = PixverseMCPServer(config_path=config_path)
        await server.initialize(config_path)
        await server.run()


async def cli_main():
    """CLI entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pixverse MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--sse", action="store_true", help="Run SSE server instead of stdio")
    parser.add_argument("--port", type=int, default=8080, help="Port for SSE server")
    
    args = parser.parse_args()
    config_path = args.config
    mode = "sse" if args.sse else "stdio"
    
    await main(config_path=config_path, mode=mode)


if __name__ == "__main__":
    asyncio.run(cli_main())
