"""PixVerse MCP server implementation with video generation tools."""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .validate import (
    validate_aspect_ratio,
    validate_duration,
    validate_quality,
    validate_motion_mode,
    validate_model,
    validate_seed
)
from .req_client import make_pixverse_request, poll_video_status
from .const import API_BASE_URL

# Set logging output to stderr (stdout is reserved for MCP communication)
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pixverse-mcp")

# Initialize FastMCP server
mcp = FastMCP("pixverse-video")

# MCP tool implementations

@mcp.tool()
async def generate_text_to_video(
    prompt: str,
    aspect_ratio: str = "16:9",
    duration: int = 5,
    model: str = "v3.5",
    motion_mode: str = "normal",
    negative_prompt: str = "",
    quality: str = "540p",
    seed: int = 0,
    template_id: Optional[int] = None,
    water_mark: bool = False
) -> str:
    """Generate video from text prompt using PixVerse API.

    Args:
        prompt: Main text prompt describing the video to generate
        aspect_ratio: Video aspect ratio (16:9, 4:3, 1:1, 3:4, 9:16)
        duration: Video duration in seconds (5 or 8)
        model: Model version to use (v3.5)
        motion_mode: Motion intensity (normal, fast)
        negative_prompt: Prompt for elements to avoid in the video
        quality: Video quality (360p, 540p, 720p, 1080p)
        seed: Randomization seed (0-2147483647)
        template_id: Optional template ID
        water_mark: Whether to include watermark

    Returns:
        Generated video information including download URL
    """
    try:
        # Log tool invocation
        logger.info(f"Text-to-video tool called: {prompt}")

        # Validate parameters
        aspect_ratio = validate_aspect_ratio(aspect_ratio)
        duration = validate_duration(duration, quality)
        quality = validate_quality(quality)
        motion_mode = validate_motion_mode(motion_mode)
        model = validate_model(model)
        seed = validate_seed(seed)

        # Prepare request data
        request_data = {
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "model": model,
            "motion_mode": motion_mode,
            "negative_prompt": negative_prompt,
            "prompt": prompt,
            "quality": quality,
            "seed": seed,
            "water_mark": water_mark
        }

        # Add template_id only if provided
        if template_id is not None:
            request_data["template_id"] = template_id

        # Send API request to generate video
        logger.info(f"Initiating text-to-video generation: {prompt}")
        generation_response = await make_pixverse_request("video/text/generate", method="POST", data=request_data)

        # Check API response
        if generation_response.get("ErrCode") != 0:
            error_message = generation_response.get("ErrMsg", "Unknown error")
            logger.error(f"Text-to-video generation failed: {error_message}")
            return f"Video generation failed: {error_message}"

        # Get video_id from Resp
        video_id = generation_response.get("Resp", {}).get("video_id")
        if not video_id:
            logger.error("API did not return a video ID")
            return "Video generation failed: No video ID returned"

        # Poll for completion status
        logger.info(f"Polling video status, ID: {video_id}")
        status_data = await poll_video_status(video_id)

        # Extract results
        video_data = status_data.get("Resp", {})
        video_url = video_data.get("url")  # Note: API returns "url" field

        if not video_url:
            logger.error("No video URL returned in result")
            return "Video generation completed but no URL provided"

        # Build result object
        result = {
            "video_id": video_id,
            "status": "Completed",
            "video_url": video_url,
            "prompt": prompt,
            "settings": {
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "quality": quality,
                "motion_mode": motion_mode
            },
            "details": {
                "create_time": video_data.get("create_time"),
                "modify_time": video_data.get("modify_time"),
                "resolution": f"{video_data.get('outputWidth')}x{video_data.get('outputHeight')}",
                "seed": video_data.get("seed")
            }
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except ValueError as e:
        # Parameter validation errors
        logger.error(f"Parameter validation error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        # Other errors
        logger.error(f"Text-to-video generation error: {str(e)}")
        return f"Error generating video: {str(e)}"


@mcp.tool()
async def upload_image_from_path(
    image_path: str
) -> str:
    """Upload an image to PixVerse API from a local file path.

    Args:
        image_path: Path to the local image file (must be an absolute path)

    Returns:
        Upload result including image ID and image URL
    """
    try:
        # Log tool invocation
        logger.info(f"Image upload from path tool called: {image_path}")

        # Validate file existence
        if not os.path.exists(image_path):
            error_message = f"File does not exist: {image_path}"
            logger.error(error_message)
            return f"Error: {error_message}"
            
        if not os.path.isfile(image_path):
            error_message = f"Path is not a file: {image_path}"
            logger.error(error_message)
            return f"Error: {error_message}"

        # Validate supported image format
        supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(image_path)[1].lower()
        if file_extension not in supported_extensions:
            error_message = f"Unsupported image format: {file_extension}. Supported formats: {', '.join(supported_extensions)}"
            logger.error(error_message)
            return f"Error: {error_message}"

        # Get filename
        image_name = os.path.basename(image_path)

        # Read image file
        try:
            with open(image_path, "rb") as image_file:
                # Read file content
                image_data = image_file.read()
                
                # Create file object for API request
                files = {'image': (image_name, image_data)}
                
                # Send API request
                logger.info(f"Uploading image {image_name} to PixVerse API")
                upload_response = await make_pixverse_request("image/upload", method="POST", files=files)
        except IOError as e:
            error_message = f"Error reading file: {str(e)}"
            logger.error(error_message)
            return f"Error: {error_message}"

        # Check upload response
        if upload_response.get("ErrCode") != 0:
            error_message = upload_response.get("ErrMsg", "Unknown error")
            logger.error(f"Image upload failed: {error_message}")
            return f"Image upload failed: {error_message}"

        # Get img_id and img_url from Resp
        resp_data = upload_response.get("Resp", {})
        img_id = resp_data.get("img_id")
        img_url = resp_data.get("img_url")
        
        if not img_id:
            logger.error("API did not return an image ID")
            return "Image upload failed: No image ID returned"

        # Get file info
        file_stats = os.stat(image_path)
        file_size = file_stats.st_size
        file_size_display = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"

        # Build result object
        result = {
            "img_id": img_id,
            "img_url": img_url,
            "status": "Upload successful",
            "filename": image_name,
            "filepath": image_path,
            "filesize": file_size_display,
            "file_extension": file_extension
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        # Other errors
        logger.error(f"Error uploading image from path: {str(e)}")
        return f"Error uploading image: {str(e)}"
    
    
@mcp.tool()
async def generate_image_to_video(
    img_id: str,
    prompt: str,
    duration: int = 5,
    model: str = "v3.5",
    motion_mode: str = "normal",
    negative_prompt: str = "",
    quality: str = "540p",
    seed: int = 0,
    water_mark: bool = False
) -> str:
    """Generate video from an uploaded image using PixVerse API.

    Args:
        img_id: ID of the uploaded image (returned by upload_image tool)
        prompt: Text prompt to guide video generation
        duration: Video duration in seconds (5 or 8)
        model: Model version to use (v3.5)
        motion_mode: Motion intensity (normal, fast)
        negative_prompt: Prompt for elements to avoid in the video
        quality: Video quality (360p, 540p, 720p, 1080p)
        seed: Randomization seed (0-2147483647)
        water_mark: Whether to include watermark

    Returns:
        Generated video information including download URL
    """
    try:
        # Log tool invocation
        logger.info(f"Image-to-video tool called with image ID: {img_id}")

        # Validate parameters
        duration = validate_duration(duration, quality)
        quality = validate_quality(quality)
        motion_mode = validate_motion_mode(motion_mode)
        model = validate_model(model)
        seed = validate_seed(seed)

        # Step: Generate video from uploaded image
        request_data = {
            "duration": duration,
            "img_id": img_id,
            "model": model,
            "motion_mode": motion_mode,
            "negative_prompt": negative_prompt,
            "prompt": prompt,
            "quality": quality,
            "seed": seed,
            "water_mark": water_mark
        }

        logger.info(f"Initiating image-to-video generation with img_id: {img_id}")
        generation_response = await make_pixverse_request("video/img/generate", method="POST", data=request_data)

        # Check generation response
        if generation_response.get("ErrCode") != 0:
            error_message = generation_response.get("ErrMsg", "Unknown error")
            logger.error(f"Image-to-video generation failed: {error_message}")
            return f"Video generation failed: {error_message}"

        # Get video_id from Resp
        video_id = generation_response.get("Resp", {}).get("video_id")
        if not video_id:
            logger.error("API did not return a video ID")
            return "Video generation failed: No video ID returned"

        # Poll for completion status
        logger.info(f"Polling video status, ID: {video_id}")
        status_data = await poll_video_status(video_id)

        # Extract results
        video_data = status_data.get("Resp", {})
        video_url = video_data.get("url")  # Note: API returns "url" field

        if not video_url:
            logger.error("No video URL returned in result")
            return "Video generation completed but no URL provided"

        # Build result object
        result = {
            "video_id": video_id,
            "status": "Completed",
            "video_url": video_url,
            "prompt": prompt,
            "img_id": img_id,
            "settings": {
                "duration": duration,
                "quality": quality,
                "motion_mode": motion_mode
            },
            "details": {
                "create_time": video_data.get("create_time"),
                "modify_time": video_data.get("modify_time"),
                "resolution": f"{video_data.get('outputWidth')}x{video_data.get('outputHeight')}",
                "seed": video_data.get("seed")
            }
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except ValueError as e:
        # Parameter validation errors
        logger.error(f"Parameter validation error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        # Other errors
        logger.error(f"Image-to-video generation error: {str(e)}")
        return f"Error generating video: {str(e)}"

@mcp.tool()
async def get_video_status(video_id: int) -> str:
    """Check the status of a video generation task.

    Args:
        video_id: ID of the video generation task

    Returns:
        Current status information about video generation
    """
    try:
        # Log tool invocation
        logger.info(f"Video status tool called, ID: {video_id}")

        logger.info(f"Checking status for video ID: {video_id}")
        status_data = await make_pixverse_request(f"video/result/{video_id}")

        # Check status response
        if status_data.get("ErrCode") != 0:
            error_message = status_data.get("ErrMsg", "Unknown error")
            logger.error(f"Status check failed: {error_message}")
            return f"Status check failed: {error_message}"

        # Get status information from Resp
        video_data = status_data.get("Resp", {})
        status_code = video_data.get("status")
        status_message = "Unknown"

        if status_code == 1:
            status_message = "Completed"
        elif status_code == 5:
            status_message = "Processing"
        else:
            status_message = f"Other status ({status_code})"

        # Build more detailed result
        result = {
            "video_id": video_id,
            "status_code": status_code,
            "status": status_message,
            "url": video_data.get("url"),
            "prompt": video_data.get("prompt"),
            "negative_prompt": video_data.get("negative_prompt"),
            "resolution": f"{video_data.get('outputWidth')}x{video_data.get('outputHeight')}",
            "create_time": video_data.get("create_time"),
            "modify_time": video_data.get("modify_time"),
            "seed": video_data.get("seed"),
            "file_size": video_data.get("size")
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error checking video status: {str(e)}")
        return f"Error checking video status: {str(e)}"

# Main function to be used as entry point
def main():
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Check environment variables
    if "PIXVERSE_API_KEY" not in os.environ:
        logger.warning("PIXVERSE_API_KEY environment variable not set. Using default value from documentation.")
        print("Warning: PIXVERSE_API_KEY environment variable not set, using default value", file=sys.stderr)

    # Print startup information to stderr instead of stdout
    print("PixVerse Video MCP Server starting...", file=sys.stderr)
    print(f"API key: {'Set' if 'PIXVERSE_API_KEY' in os.environ else 'Using default value'}", file=sys.stderr)

    try:
        # Run server
        logger.info("Starting PixVerse Video MCP Server")
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Error starting server: {str(e)}", file=sys.stderr)
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    main()