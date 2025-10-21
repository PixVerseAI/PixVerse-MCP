"""
SSE (Server-Sent Events) server implementation for Pixverse MCP.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from loguru import logger

from .server import PixverseMCPServer
from .client import PixverseClient
from .models.responses import VideoStatus


class PixverseSSEServer:
    """SSE server for Pixverse MCP with real-time notifications."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.mcp_server = PixverseMCPServer(config_path)
        self.clients: Dict[str, asyncio.Queue] = {}
        self.video_tasks: Dict[int, str] = {}  # video_id -> client_id
        
    async def initialize(self):
        """Initialize the MCP server."""
        await self.mcp_server.initialize()
        
    async def add_client(self, client_id: str) -> asyncio.Queue:
        """Add a new SSE client."""
        queue = asyncio.Queue()
        self.clients[client_id] = queue
        logger.info(f"SSE client connected: {client_id}")
        return queue
        
    async def remove_client(self, client_id: str):
        """Remove an SSE client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"SSE client disconnected: {client_id}")
            
    async def broadcast_notification(self, event_type: str, data: Dict[str, Any]):
        """Broadcast notification to all connected clients."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Send to all clients
        for client_id, queue in self.clients.items():
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Failed to send notification to client {client_id}: {e}")
                
    async def send_to_client(self, client_id: str, event_type: str, data: Dict[str, Any]):
        """Send notification to a specific client."""
        if client_id not in self.clients:
            return
            
        message = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            await self.clients[client_id].put(message)
        except Exception as e:
            logger.error(f"Failed to send notification to client {client_id}: {e}")
            
    async def monitor_video_progress(self, video_id: int, client_id: str):
        """Monitor video generation progress and send updates."""
        try:
            self.video_tasks[video_id] = client_id
            
            # Send initial notification
            await self.send_to_client(client_id, "video_started", {
                "video_id": video_id,
                "status": "pending",
                "message": "Video generation started"
            })
            
            # Monitor progress
            max_attempts = 120  # 20 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                
                try:
                    result = await self.mcp_server.client.get_video_result(video_id)
                    
                    # Send progress update
                    await self.send_to_client(client_id, "video_progress", {
                        "video_id": video_id,
                        "status": result.status.value if hasattr(result.status, 'value') else str(result.status),
                        "attempt": attempt,
                        "max_attempts": max_attempts
                    })
                    
                    if result.status.name == "COMPLETED":
                        await self.send_to_client(client_id, "video_completed", {
                            "video_id": video_id,
                            "status": "completed",
                            "video_url": result.video_url,
                            "output_width": result.outputWidth,
                            "output_height": result.outputHeight,
                            "size": result.size,
                            "has_audio": result.has_audio
                        })
                        break
                    elif result.status.name == "FAILED":
                        await self.send_to_client(client_id, "video_failed", {
                            "video_id": video_id,
                            "status": "failed",
                            "message": "Video generation failed"
                        })
                        break
                    
                    # Wait before next check
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.error(f"Error monitoring video {video_id}: {e}")
                    await self.send_to_client(client_id, "video_error", {
                        "video_id": video_id,
                        "status": "error",
                        "message": str(e)
                    })
                    break
            
            if attempt >= max_attempts:
                await self.send_to_client(client_id, "video_timeout", {
                    "video_id": video_id,
                    "status": "timeout",
                    "message": "Video generation timed out"
                })
                
        finally:
            # Clean up
            if video_id in self.video_tasks:
                del self.video_tasks[video_id]


def create_sse_app(config_path: Optional[str] = None) -> FastAPI:
    """Create FastAPI app with SSE support."""
    
    sse_server = PixverseSSEServer(config_path)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        await sse_server.initialize()
        logger.info("🚀 Pixverse SSE Server started")
        yield
        # Shutdown
        logger.info("👋 Pixverse SSE Server stopped")
    
    app = FastAPI(
        title="Pixverse MCP SSE Server",
        description="Server-Sent Events interface for Pixverse video generation",
        version="1.0.0",
        lifespan=lifespan
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with server info."""
        return {
            "name": "Pixverse MCP SSE Server",
            "version": "1.0.0",
            "endpoints": {
                "sse": "/events",
                "generate_text_video": "/api/text-to-video",
                "generate_image_video": "/api/image-to-video",
                "upload_image": "/api/upload-image",
                "video_status": "/api/video/{video_id}/status"
            }
        }
    
    @app.get("/events")
    async def sse_endpoint(request: Request):
        """SSE endpoint for real-time notifications."""
        client_id = str(uuid.uuid4())
        
        async def event_generator():
            queue = await sse_server.add_client(client_id)
            
            try:
                # Send welcome message
                yield {
                    "event": "connected",
                    "data": json.dumps({
                        "client_id": client_id,
                        "message": "Connected to Pixverse SSE server"
                    })
                }
                
                # Stream events
                while True:
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield {
                            "event": message["type"],
                            "data": json.dumps(message["data"])
                        }
                    except asyncio.TimeoutError:
                        # Send heartbeat
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})
                        }
                        
            except Exception as e:
                logger.error(f"SSE stream error for client {client_id}: {e}")
            finally:
                await sse_server.remove_client(client_id)
        
        return EventSourceResponse(event_generator())
    
    @app.post("/api/text-to-video")
    async def generate_text_video(request: Request):
        """Generate video from text with SSE notifications."""
        try:
            data = await request.json()
            client_id = request.headers.get("X-Client-ID")
            
            if not client_id:
                raise HTTPException(status_code=400, detail="X-Client-ID header required")
            
            # Call MCP server
            result = await sse_server.mcp_server.call_tool("text_to_video", data)
            
            if "video_id" in result.content[0].text:
                video_data = json.loads(result.content[0].text)
                video_id = video_data["video_id"]
                
                # Start monitoring in background
                asyncio.create_task(sse_server.monitor_video_progress(video_id, client_id))
                
                return {"video_id": video_id, "status": "started"}
            else:
                raise HTTPException(status_code=500, detail="Failed to start video generation")
                
        except Exception as e:
            logger.error(f"Text-to-video generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/image-to-video")
    async def generate_image_video(request: Request):
        """Generate video from image with SSE notifications."""
        try:
            data = await request.json()
            client_id = request.headers.get("X-Client-ID")
            
            if not client_id:
                raise HTTPException(status_code=400, detail="X-Client-ID header required")
            
            # Call MCP server
            result = await sse_server.mcp_server.call_tool("image_to_video", data)
            
            if "video_id" in result.content[0].text:
                video_data = json.loads(result.content[0].text)
                video_id = video_data["video_id"]
                
                # Start monitoring in background
                asyncio.create_task(sse_server.monitor_video_progress(video_id, client_id))
                
                return {"video_id": video_id, "status": "started"}
            else:
                raise HTTPException(status_code=500, detail="Failed to start video generation")
                
        except Exception as e:
            logger.error(f"Image-to-video generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/video/{video_id}/status")
    async def get_video_status(video_id: int):
        """Get current video status."""
        try:
            result = await sse_server.mcp_server.client.get_video_result(video_id)
            return {
                "video_id": video_id,
                "status": result.status.value if hasattr(result.status, 'value') else str(result.status),
                "video_url": result.video_url if hasattr(result, 'video_url') else None,
                "output_width": result.outputWidth if hasattr(result, 'outputWidth') else None,
                "output_height": result.outputHeight if hasattr(result, 'outputHeight') else None,
                "size": result.size if hasattr(result, 'size') else None,
                "has_audio": result.has_audio if hasattr(result, 'has_audio') else None
            }
        except Exception as e:
            logger.error(f"Get video status error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def run_sse_server(config_path: Optional[str] = None, host: str = "0.0.0.0", port: int = 8080):
    """Run the SSE server."""
    import uvicorn
    
    app = create_sse_app(config_path)
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    await server.serve()
