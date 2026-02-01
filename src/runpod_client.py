"""Async HTTP client for Runpod APIs."""

import asyncio
import logging
from typing import Any

import aiohttp


logger = logging.getLogger(__name__)


class RunpodClient:
    """Shared async HTTP client for Runpod APIs."""

    def __init__(self, api_key: str):
        """Initialize client with API key.

        Args:
            api_key: Runpod API key for authentication
        """
        self.api_key = api_key
        self.base_url = "https://api.runpod.ai/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    async def submit_job(
        self,
        endpoint_id: str,
        input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit a job to the /run endpoint.

        Args:
            endpoint_id: Runpod endpoint ID
            input_data: Job input parameters

        Returns:
            Response containing job_id and status

        Raises:
            aiohttp.ClientError: If API request fails
        """
        url = f"{self.base_url}/{endpoint_id}/run"
        payload = {"input": input_data}

        logger.info(f"Submitting job to {endpoint_id}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 401:
                        raise RuntimeError(
                            "Invalid API key. Check RUNPOD_API_KEY environment variable."
                        )
                    elif response.status == 404:
                        raise RuntimeError(
                            f"Invalid endpoint ID '{endpoint_id}'. "
                            "Check your endpoint configuration."
                        )

                    response.raise_for_status()
                    result = await response.json()

                    job_id = result.get("id")
                    logger.info(f"Job submitted: {job_id}")

                    return result

        except asyncio.TimeoutError:
            raise RuntimeError(
                "Request timeout. Check internet connection and try again."
            )
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {str(e)}")

    async def get_status(
        self,
        endpoint_id: str,
        job_id: str
    ) -> dict[str, Any]:
        """Get job status from /status endpoint.

        Args:
            endpoint_id: Runpod endpoint ID
            job_id: Job ID to check

        Returns:
            Response containing job status and output

        Raises:
            aiohttp.ClientError: If API request fails
        """
        url = f"{self.base_url}/{endpoint_id}/status/{job_id}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 401:
                        raise RuntimeError(
                            "Invalid API key. Check RUNPOD_API_KEY environment variable."
                        )
                    elif response.status == 404:
                        raise RuntimeError(
                            f"Job '{job_id}' not found. Verify job ID and endpoint type."
                        )

                    response.raise_for_status()
                    return await response.json()

        except asyncio.TimeoutError:
            raise RuntimeError(
                "Request timeout. Check internet connection and try again."
            )
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error: {str(e)}")

    async def poll_until_complete(
        self,
        endpoint_id: str,
        job_id: str,
        max_wait: int = 300
    ) -> dict[str, Any]:
        """Poll job status with exponential backoff until completion or timeout.

        Args:
            endpoint_id: Runpod endpoint ID
            job_id: Job ID to poll
            max_wait: Maximum seconds to wait (default: 300)

        Returns:
            Completed job result

        Raises:
            TimeoutError: If job exceeds max_wait
            RuntimeError: If job fails
        """
        # Exponential backoff: 2s, 4s, 8s, then 15s repeatedly
        delays = [2, 4, 8] + [15] * 20  # Total ~320s possible
        elapsed = 0

        logger.info(f"Polling job {job_id} (max wait: {max_wait}s)")

        for i, delay in enumerate(delays):
            if elapsed >= max_wait:
                logger.warning(f"Job {job_id} exceeded {max_wait}s timeout")
                raise TimeoutError(
                    f"Job {job_id} exceeded {max_wait}s timeout"
                )

            await asyncio.sleep(delay)
            elapsed += delay

            result = await self.get_status(endpoint_id, job_id)
            status = result.get("status")

            logger.info(f"Poll #{i+1}: {status} (elapsed: {elapsed}s)")

            if status == "COMPLETED":
                logger.info(f"Job {job_id} completed successfully")
                return result
            elif status == "FAILED":
                error_msg = result.get("error", "Unknown error")
                # Try to extract more detailed error from output
                if "output" in result and isinstance(result["output"], dict):
                    error_msg = result["output"].get("error", error_msg)

                logger.error(f"Job {job_id} failed: {error_msg}")
                raise RuntimeError(f"Job failed: {error_msg}")
            elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                # Continue polling
                continue
            else:
                logger.warning(f"Unknown status '{status}' for job {job_id}")

        logger.warning(f"Job {job_id} exceeded maximum polling attempts")
        raise TimeoutError(
            f"Job {job_id} exceeded {max_wait}s timeout"
        )
