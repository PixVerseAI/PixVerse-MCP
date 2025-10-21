"""
Base HTTP client for Pixverse API.
"""

import asyncio
import uuid
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..exceptions import (
    PixverseAPIError,
    PixverseAuthError,
    PixverseConnectionError,
    PixverseRateLimitError,
    PixverseTimeoutError,
)
from ..models.responses import APIResponse, ErrorResponse


class BaseClient:
    """Base HTTP client for Pixverse API interactions."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://app-api.pixverseai.cn",
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60,
    ):
        """
        Initialize the base client.

        Args:
            api_key: Pixverse API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_per_minute: Rate limit per minute
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create HTTP client with default headers
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._get_default_headers(),
        )

        # Rate limiting
        self._rate_limiter = asyncio.Semaphore(rate_limit_per_minute)
        self._last_request_time = 0.0

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "API-KEY": self.api_key,
            "Accept": "application/json",
            "User-Agent": "pixverse-mcp/0.1.0",
        }

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID for request tracking."""
        return str(uuid.uuid4())

    async def _handle_rate_limit(self) -> None:
        """Handle rate limiting."""
        async with self._rate_limiter:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_request_time

            # Ensure minimum interval between requests (1 second)
            min_interval = 60.0 / 60  # 1 request per second
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)

            self._last_request_time = asyncio.get_event_loop().time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_form_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            PixverseAPIError: For API errors
            PixverseAuthError: For authentication errors
            PixverseRateLimitError: For rate limit errors
            PixverseTimeoutError: For timeout errors
            PixverseConnectionError: For connection errors
        """
        await self._handle_rate_limit()

        # Prepare request
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        request_headers = self._get_default_headers()
        request_headers["Ai-Trace-Id"] = self._generate_trace_id()
        
        # Set Content-Type for JSON requests (but not for form data)
        if data is not None and not use_form_data:
            request_headers["Content-Type"] = "application/json"

        if headers:
            request_headers.update(headers)

        logger.debug(f"Making {method} request to {url}")

        try:
            if use_form_data and data:
                # Send as form data
                response = await self._client.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    headers=request_headers,
                )
            else:
                # Send as JSON
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                )

            # Handle different response status codes
            if response.status_code == 200:
                response_data = response.json()

                # Check for API-level errors in response
                if isinstance(response_data, dict):
                    err_code = response_data.get("ErrCode", 0)
                    if err_code != 0:
                        err_msg = response_data.get("ErrMsg", "Unknown error")

                        # Handle specific error codes
                        if err_code in [10001, 10002, 10003, 10004, 10005]:
                            raise PixverseAuthError(err_msg, error_code=err_code)
                        else:
                            raise PixverseAPIError(
                                err_msg,
                                status_code=response.status_code,
                                error_code=err_code,
                                response_data=response_data,
                            )

                return response_data

            elif response.status_code == 401:
                raise PixverseAuthError("Authentication failed")
            elif response.status_code == 403:
                raise PixverseAuthError("Access forbidden")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise PixverseRateLimitError(
                    "Rate limit exceeded",
                    retry_after=int(retry_after) if retry_after else None,
                )
            else:
                # Try to parse error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get("ErrMsg", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"

                raise PixverseAPIError(
                    error_msg,
                    status_code=response.status_code,
                    response_data=error_data if "error_data" in locals() else None,
                )

        except httpx.TimeoutException as e:
            raise PixverseTimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise PixverseConnectionError(f"Connection error: {e}")
        except httpx.HTTPError as e:
            raise PixverseConnectionError(f"HTTP error: {e}")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_form_data: bool = False,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, data=data, headers=headers, use_form_data=use_form_data)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, data=data, headers=headers)

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, headers=headers)

    async def upload_file(
        self,
        endpoint: str,
        file_path: str,
        field_name: str = "file",
        additional_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file using multipart/form-data.

        Args:
            endpoint: API endpoint
            file_path: Path to the file to upload
            field_name: Form field name for the file
            additional_data: Additional form data
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        import os
        from pathlib import Path

        await self._handle_rate_limit()

        # Prepare request
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        request_headers = self._get_default_headers()
        request_headers["Ai-Trace-Id"] = self._generate_trace_id()

        if headers:
            request_headers.update(headers)

        logger.debug(f"Uploading file {file_path} to {url}")

        try:
            # Prepare file and form data
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            data = additional_data or {}

            with open(file_path, "rb") as file_handle:
                files = {
                    field_name: (
                        file_path_obj.name,
                        file_handle,
                        self._get_content_type(file_path_obj.suffix)
                    )
                }

                response = await self._client.request(
                    method="POST",
                    url=url,
                    files=files,
                    data=data,
                    headers=request_headers,
                )

            # Handle response same as _make_request
            if response.status_code == 200:
                response_data = response.json()

                # Check for API-level errors in response
                if isinstance(response_data, dict):
                    err_code = response_data.get("ErrCode", 0)
                    if err_code != 0:
                        err_msg = response_data.get("ErrMsg", "Unknown error")

                        # Handle specific error codes
                        if err_code in [10001, 10002, 10003, 10004, 10005]:
                            raise PixverseAuthError(err_msg, error_code=err_code)
                        else:
                            raise PixverseAPIError(
                                err_msg,
                                status_code=response.status_code,
                                error_code=err_code,
                                response_data=response_data,
                            )

                return response_data

            elif response.status_code == 401:
                raise PixverseAuthError("Authentication failed")
            elif response.status_code == 403:
                raise PixverseAuthError("Access forbidden")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise PixverseRateLimitError(
                    "Rate limit exceeded",
                    retry_after=int(retry_after) if retry_after else None,
                )
            else:
                # Try to parse error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get("ErrMsg", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"

                raise PixverseAPIError(
                    error_msg,
                    status_code=response.status_code,
                    response_data=error_data if "error_data" in locals() else None,
                )

        except httpx.TimeoutException as e:
            raise PixverseTimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise PixverseConnectionError(f"Connection error: {e}")
        except httpx.HTTPError as e:
            raise PixverseConnectionError(f"HTTP error: {e}")

    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension."""
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".avi": "video/avi",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
        }
        return content_types.get(file_extension.lower(), "application/octet-stream")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
