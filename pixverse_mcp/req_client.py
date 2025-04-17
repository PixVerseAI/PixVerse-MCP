"""PixVerse API client functions."""

import os
import uuid
import json
import asyncio
import httpx
import logging
import sys
from urllib.parse import urljoin
from typing import Dict, Any, Optional, List

from const import API_BASE_URL, POLL_INTERVAL, API_KEY

# Set up logger
logger = logging.getLogger("pixverse-mcp")

# API request helper function
async def make_pixverse_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, 
                               files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Send request to PixVerse API with appropriate error handling"""
    global API_KEY
    
    # 如果API_KEY未初始化，则从MCP配置获取
    if API_KEY is None:
        API_KEY = os.environ.get("PIXVERSE_API_KEY")
            
    # Validate API key is set
    if not API_KEY:
        error_message = "PIXVERSE_API_KEY 未在MCP配置或环境变量中设置。请在启动MCP服务器前配置此密钥。"
        logger.error(error_message)
        raise Exception(error_message)
        
    url = urljoin(API_BASE_URL, endpoint)
    headers = {
        "API-KEY": API_KEY,
        "Ai-trace-id": str(uuid.uuid4())
    }

    if data and not files:
        headers["Content-Type"] = "application/json"

    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method == "POST":
                if files:
                    response = await client.post(url, headers=headers, files=files, timeout=60.0)
                else:
                    response = await client.post(url, headers=headers, json=data, timeout=60.0)

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"PixVerse API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Error communicating with PixVerse API: {str(e)}")
        raise Exception(f"Error communicating with PixVerse API: {str(e)}")
    

    
async def poll_video_status(video_id: int) -> Dict[str, Any]:
    """Poll video generation status until completion or failure"""
    max_attempts = 60  # Max 5 minutes (5s * 60)
    attempts = 0

    while attempts < max_attempts:
        status_data = await make_pixverse_request(f"video/result/{video_id}")
        
        # 打印完整的API响应
        logger.info(f"API响应详情: {json.dumps(status_data, indent=2, ensure_ascii=False)}")

        # Check if API response is successful
        if status_data.get("ErrCode") != 0:
            error_message = status_data.get("ErrMsg", "Unknown error")
            logger.error(f"Failed to get video status: {error_message}")
            raise Exception(f"Failed to get video status: {error_message}")

        # Get status information from Resp
        video_data = status_data.get("Resp", {})
        # 打印视频数据详情
        logger.info(f"视频数据详情: {json.dumps(video_data, indent=2, ensure_ascii=False)}")
        status_code = video_data.get("status")

        # Check if video is complete (status 1) or failed
        if status_code == 1:
            logger.info(f"Video generation complete: {video_id}")
            return status_data
        elif status_code not in [5]:  # 5 means processing
            logger.error(f"Video generation failed: status code {status_code}")
            raise Exception(f"Video generation failed: status code {status_code}")

        logger.info(f"Video still processing, attempt {attempts+1}/{max_attempts}, status code: {status_code}, video_id: {video_id}")
        await asyncio.sleep(POLL_INTERVAL)
        attempts += 1

    raise Exception("Video generation timed out after 5 minutes")