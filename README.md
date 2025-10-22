# PixVerse MCP
<div align="left">
<a href="https://app.pixverse.ai" style="margin: 2px">
<img alt="Webapp" src="https://img.shields.io/badge/PixVerse-Web-3961F1?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
</a>
<a href="https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp" style="margin: 2px">
<img alt="API" src="https://img.shields.io/badge/PixVerse-API-3961F1?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
</a>
</div>

A comprehensive tool that allows you to access PixVerse's latest video generation models via applications that support the Model Context Protocol (MCP), such as Claude or Cursor. Generate videos from text, animate images, create transitions, add lip sync, sound effects, and much more!

[中文文档](https://github.com/PixVerseAI/PixVerse-MCP/blob/main/README-CN.md)


https://github.com/user-attachments/assets/08ce90b7-2591-4256-aff2-9cc51e156d00


## Overview

PixVerse MCP is a powerful tool that enables you to access PixVerse's latest video generation models through applications that support the Model Context Protocol (MCP). This integration allows you to generate high-quality videos with advanced features including text-to-video, image-to-video, video extensions, transitions, lip sync, sound effects, and more.

## Key Features

- **Text-to-Video Generation**: Generate creative videos using text prompts
- **Image-to-Video Animation**: Animate static images into dynamic videos
- **Flexible Parameter Control**: Adjust video quality, length, aspect ratio, and more
- **Video Extension**: Extend existing videos seamlessly for longer sequences
- **Scene Transitions**: Create smooth morphing between different images
- **Lip Sync**: Add realistic lip sync to talking head videos with TTS or custom audio
- **Sound Effects**: Generate contextual sound effects based on video content
- **Fusion Video**: Composite multiple subjects into one scene (v4.5 only)
- **Resource Management**: Upload images and videos from local files or URLs
- **Co-Creation with AI Assistants**: Collaborate with AI models like Claude to enhance your creative workflow

## System Components

The system consists of two main components:

1. **UVX MCP Server**
   - Python-based cloud server
   - Communicates directly with the PixVerse API
   - Provides full video generation capabilities

## Installation & Configuration

### Prerequisites

1. Python 3.10 or higher
2. UV/UVX
3. PixVerse API Key: Obtain from PixVerse Platform (This feature requires API Credits, which must be purchased separately on [PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)


### Get Dependencies

1. **Python**:
   - Download and install from the official Python website
   - Ensure Python is added to your system path

2. **UV/UVX**:
   - Install uv and set up our Python project and environment:

#### Mac/Linux
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## How to Use MCP Server

### 1. Get PixVerse API Key
- Visit the [PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)
- Register or log into your account
- Create and copy your API key from the account settings
- [API key generation guide](https://docs.platform.pixverse.ai/how-to-get-api-key-882968m0)

### 2. Download Required Dependencies
- **Python**: Install Python 3.10 or above
- **UV/UVX**: Install the latest stable version of UV & UVX

### 3. Configure MCP Client
- Open your MCP client (e.g., Claude for Desktop or Cursor)
- Locate the client settings
- Open mcp_config.json (or relevant config file)
- Add the configuration based on the method you use:

```json
{
  "mcpServers": {
    "PixVerse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp"
      ],
      "env": {
        "PIXVERSE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

- Add the API key obtained from platform.pixverse.ai under `"PIXVERSE_API_KEY": "xxxx"`
- Save the config file

### 5. Restart MCP Client or Refresh MCP Server
- Fully close and reopen your MCP client
- Or use the "Refresh MCP Server" option if supported

## Client-specific Configuration

### Claude for Desktop

1. Open the Claude application
2. Navigate to Claude > Settings > Developer > Edit Config
3. Open the claude_desktop_config.json file
   - Windows
   - Mac : ~/Library/Application\ Support/Claude/claude_desktop_config.json
4. Add the configuration above and save
5. Restart Claude
   - If connected successfully: the homepage will not show any error and the MCP status will be green
   - If connection fails: an error message will be shown on the homepage

### Cursor

1. Open the Cursor application
2. Go to Settings > Model Context Protocol
3. Add a new server
4. Fill in the server details as in the JSON config above
5. Save and restart or refresh the MCP server

## Advanced Usage Example

### Text-to-Video

Use natural language prompts via Claude or Cursor to generate videos.

**Basic Example**:
```
Generate a video of a sunset over the ocean. Golden sunlight reflects on the water as waves gently hit the shore.
```

**Advanced Example with Parameters**:
```
Generate a night cityscape video with the following parameters:
Content: Skyscraper lights twinkling under the night sky, with car lights forming streaks on the road
Aspect Ratio: 16:9
Quality: 540p
Duration: 5 seconds
Motion Mode: normal
Negative Prompts: blur, shaking, text
```

**Supported Parameters**:
- Aspect Ratio: 16:9, 4:3, 1:1, 3:4, 9:16
- Duration: 5s or 8s
- Quality: 360p, 540p, 720p, 1080p
- Motion Mode: normal or fast

### Script + Video

Use detailed scene descriptions or shot lists to create more structured videos.

**Scene Description Example**:
```
Scene: A beach in the early morning.
The sun is rising, casting golden reflections on the sea.
Footprints stretch across the sand.
Gentle waves leave white foam as they retreat.
A small boat slowly sails across the calm sea in the distance.
Aspect Ratio: 16:9, Quality: 540p, Duration: 5 seconds.
```

**Shot-by-Shot Example**:
```
Generate a video based on this storyboard:
- Start: Top-down shot of a coffee cup with steam rising
- Close-up: Ripples and texture on the coffee surface
- Transition: Stirring creates a vortex
- End: An open book and glasses next to the cup
Format: 1:1 square, Quality: 540p, Motion: fast
```
- Claude Desktop also supports storyboard image input.

### One-Click Video

Quickly generate videos of specific themes or styles without detailed descriptions.

**Theme Example**:
```
Generate a video with a futuristic technology theme, including neon lights and holographic projections.
```

**Style Example**:
```
Generate a watercolor-style video of blooming flowers with bright, dreamy colors.
```

### Creative + Video

Combine AI's creativity with video generation.

**Style Transfer Example**:
```
This is a photo of a cityscape. Reinterpret it with a retro style and provide a video prompt.
```

**Story Prompt Example**:
```
If this street photo is the opening scene of a movie, what happens next? Provide a short video concept.
```

**Emotional Scene Example**:
```
Look at this forest path photo and design a short video concept, either a micro-story or a scene with emotional progression.
```


## Feature Usage Gudie
### Text-to-Video
```
Generate a sunset ocean video with golden sunlight reflecting on the water
```
**Example with parameters**:
```
Prompt: "A majestic eagle soaring over mountain peaks at sunrise"
Quality: 720p
Duration: 5
Model: v5
Aspect Ratio: 16:9
```
**Parameters**: Quality(360p-1080p), Duration(5s/8s), Aspect Ratio(16:9/1:1/9:16), model(v4.5/v5)

### Image-to-Video
```
1. Upload image → Get img_id
2. Use img_id to generate animated video
```
**Example with parameters**:
```
Prompt: "The character walks through a magical forest with glowing trees"
img_id: 12345
Quality: 720p
Duration: 5s
Model: v5
```

### Video Extension
```
Use source_video_id to extend existing video
```
**Example with parameters**:
```
Prompt: "The scene continues with the character discovering a hidden cave"
source_video_id: 67890
Duration: 5s
Quality: 720p
Model: v5
```

### Scene Transitions
```
Upload two images to create smooth morphing animation
```
**Example with parameters**:
```
Prompt: "Transform from sunny beach to stormy night sky"
first_frame_img: 11111
last_frame_img: 22222
Duration: 5s
Quality: 720p
Model: v5
```

### Lip Sync
```
Video: 
TTS: Choose speaker + input text
Audio: Upload audio file + video
```
**Example with parameters**:
```
# Method 1: Generated Video + TTS
source_video_id: 33333
lip_sync_tts_speaker_id: "speaker_001"
lip_sync_tts_content: "Welcome to our amazing video tutorial"

# Method 2: Generated Video + Custom Audio
source_video_id: 33333
audio_media_id: 44444

# Method 3: Uploaded Video + TTS
video_media_id: 55555  # Upload your video first
lip_sync_tts_speaker_id: "speaker_002"
lip_sync_tts_content: "This is a custom narration"

# Method 4: Uploaded Video + Custom Audio
video_media_id: 55555  # Upload your video first
audio_media_id: 44444  # Upload your audio first
```

### Sound Effects
```
Describe effects: "Ocean waves, seagull calls, gentle wind"
```
**Example with parameters**:
```
# Method 1: Generated Video + Sound Effects
sound_effect_content: "Gentle ocean waves, seagull calls, soft wind"
source_video_id: 55555
original_sound_switch: true  # Keep original audio

# Method 2: Uploaded Video + Sound Effects
sound_effect_content: "Urban traffic, footsteps, city ambiance"
video_media_id: 66666  # Upload your video first
original_sound_switch: false  # Replace original audio

# Method 3: Replace Audio Completely
sound_effect_content: "Epic orchestral music, thunder, dramatic tension"
video_media_id: 77777  # Upload your video first
original_sound_switch: false  # Replace with new audio
```

### Fusion Video
```
Upload multiple images, use @ref_name references
Example: @person standing in front of @city with @drone flying overhead
```
**Example with parameters**:
```
Prompt: "@hero standing in front of @city with @drone flying overhead"
image_references: [
  {type: "subject", img_id: 66666, ref_name: "hero"},
  {type: "background", img_id: 77777, ref_name: "city"},
  {type: "subject", img_id: 88888, ref_name: "drone"}
]
Duration: 5s
Model:v4.5
Quality: 720p
Aspect Ratio: 16:9
```

### 📊 Status Monitoring
```
Check video_id status every 6 seconds until completion
```
**Example with parameters**:
```
video_id: 99999
# Check every 6 seconds until status becomes "completed" or "failed"
# Typical generation time: 60-120 seconds
```
**Status**: pending → in_progress → completed/failed


## FAQ

**How do I get a PixVerse API key?**
- Register at the PixVerse Platform and generate it under "API-KEY" in your account.

**What should I do if the server doesn't respond?**
1. Check whether your API key is valid
2. Ensure the configuration file path is correct
3. View error logs (typically in the log folders of Claude or Cursor)

**Does MCP support image-to-video or keyframe features?**
- Not yet. These features are only available via the PixVerse API. [API Docs](https://docs.platform.pixverse.ai)

**How to obtain credits?**
- If you haven't topped up on the API platform yet, please do so first. [PixVerse Platform](https://platform.pixverse.ai/billing?utm_source=github&utm_medium=readme&utm_campaign=mcp)

**What video formats and sizes are supported?**
- PixVerse supports resolutions from 360p to 1080p, and aspect ratios from 9:16 (portrait) to 16:9 (landscape).
- We recommend starting with 540p and 5-second videos to test the output quality.

**Where can I find the generated video?**
- You will receive a URL link to view, download, or share the video.

**How long does video generation take?**
- Typically 30 seconds to 2 minutes depending on complexity, server load, and network conditions.

**What to do if you encounter a spawn uvx ENOENT error?**
- This error is typically caused by incorrect UV/UVX installation paths. You can resolve it as follows:

For Mac/Linux:
```
sudo cp ./uvx /usr/local/bin
```

For Windows:
1. Identify the installation path of UV/UVX by running the following command in the terminal:
```
where uvx
```
2. Open File Explorer and locate the uvx/uv files.
3. Move the files to one of the following directories:
   - C:\Program Files (x86) or C:\Program Files

## Community & Support
### Community
- Join our [Discord server](https://discord.gg/pixverse) to receive updates, share creations, get help, or give feedback.

### Technical Support
- Email: api@pixverse.ai
- Website: https://platform.pixverse.ai

## Release Notes
v2.0.0 (Latest)
- **NEW**: Image-to-video animation
- **NEW**: Video extension for longer sequences
- **NEW**: Scene transitions between images
- **NEW**: Lip sync with TTS and custom audio
- **NEW**: AI-generated sound effects
- **NEW**: Fusion video for composite scenes
- **NEW**: TTS speaker selection
- **NEW**: Resource upload (images/videos) with file or url
- **NEW**: Real-time status monitoring
- **IMPROVED**: Enhanced error handling and user feedback
- **IMPROVED**: Parallel video generation support

v1.0.0
- Supports text-to-video generation via MCP
- Enables video link retrieval
- Integrates with Claude and Cursor for enhanced workflows
- Supports Cloud based Python MCP servers
