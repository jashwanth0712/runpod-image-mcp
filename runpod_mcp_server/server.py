"""MCP server for Runpod Image APIs."""

import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .config import RunpodConfig
from .runpod_client import RunpodClient
from .constants import (
    SEEDREAM_MIN_SIZE,
    SEEDREAM_MAX_SIZE,
    SEEDREAM_DEFAULT_SIZE,
    NANO_BANANA_RESOLUTIONS,
    NANO_BANANA_ASPECT_RATIOS,
    NANO_BANANA_FORMATS,
    NANO_BANANA_MIN_IMAGES,
    NANO_BANANA_MAX_IMAGES,
    NANO_BANANA_PRICING,
    SEEDREAM_INFO,
    NANO_BANANA_INFO,
    ALL_INFO,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("runpod-image-apis")

# Initialize configuration and client
try:
    config = RunpodConfig()
    client = RunpodClient(config.api_key)
    logger.info("Runpod MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize server: {e}")
    raise


def validate_size(size: str) -> tuple[bool, str]:
    """Validate Seedream image size format.

    Args:
        size: Size string like "2048*2048"

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parts = size.split("*")
        if len(parts) != 2:
            return False, (
                f"Invalid size format '{size}'. "
                f"Use format 'width*height' (e.g., '2048*2048')"
            )

        width, height = int(parts[0]), int(parts[1])

        if width < SEEDREAM_MIN_SIZE or width > SEEDREAM_MAX_SIZE:
            return False, (
                f"Invalid width {width}. "
                f"Must be between {SEEDREAM_MIN_SIZE}-{SEEDREAM_MAX_SIZE} pixels."
            )

        if height < SEEDREAM_MIN_SIZE or height > SEEDREAM_MAX_SIZE:
            return False, (
                f"Invalid height {height}. "
                f"Must be between {SEEDREAM_MIN_SIZE}-{SEEDREAM_MAX_SIZE} pixels."
            )

        return True, ""

    except (ValueError, AttributeError):
        return False, (
            f"Invalid size format '{size}'. "
            f"Use format 'width*height' with numeric values (e.g., '2048*2048')"
        )


@mcp.tool()
async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    size: str = SEEDREAM_DEFAULT_SIZE,
    seed: int = -1,
    enable_safety_checker: bool = True,
    max_wait_seconds: int = 300
) -> str:
    """Generate images from text descriptions using Seedream V4 T2I.

    This tool creates high-quality photorealistic or artistic images from text prompts.
    Jobs are processed asynchronously and typically complete in 30-90 seconds.

    Args:
        prompt: Detailed text description of the desired image. Be specific about
            style, composition, lighting, colors, and subject matter.
        negative_prompt: Elements to exclude from the image (e.g., "blurry, low quality,
            distorted faces"). Optional but recommended for better results.
        size: Image dimensions in format "width*height" (e.g., "2048*2048").
            Valid range: 1024-4096 pixels for both width and height.
            Default: "2048*2048"
        seed: Random seed for reproducibility. Use -1 for random generation (default),
            or provide a specific number to reproduce results.
        enable_safety_checker: Enable content safety filtering. Default: true.
            Set to false only if you need to bypass content filtering.
        max_wait_seconds: Maximum time to wait for job completion in seconds.
            Default: 300 (5 minutes). Increase for very large images.

    Returns:
        Success message with image URL, generation details, and job ID for status tracking.
        Format: "✓ Image generated successfully!\nURL: ...\nSize: ...\nSeed: ...\nJob ID: ..."

    Examples:
        - "A photorealistic sunset over snow-capped mountains with dramatic clouds"
        - "An oil painting of a medieval castle on a cliff, fantasy art style"
        - "Product photo of a sleek smartphone on a white background, studio lighting"
    """
    try:
        # Validate size parameter
        is_valid, error_msg = validate_size(size)
        if not is_valid:
            return f"✗ {error_msg}\nExample: '{SEEDREAM_DEFAULT_SIZE}'"

        logger.info(f"Generating image: prompt='{prompt[:50]}...', size={size}")

        # Prepare job input
        input_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "size": size,
            "seed": seed,
            "enable_safety_checker": enable_safety_checker
        }

        # Submit job
        result = await client.submit_job(config.seedream_endpoint_id, input_data)
        job_id = result.get("id")

        if not job_id:
            return "✗ Failed to submit job: No job ID returned"

        # Poll for completion
        completed = await client.poll_until_complete(
            config.seedream_endpoint_id,
            job_id,
            max_wait_seconds
        )

        # Extract result
        output = completed.get("output", {})
        image_url = output.get("result")
        actual_seed = output.get("seed", seed)

        if not image_url:
            return f"✗ Job completed but no image URL found\nJob ID: {job_id}"

        return (
            f"✓ Image generated successfully!\n"
            f"URL: {image_url}\n"
            f"Size: {size}\n"
            f"Seed: {actual_seed}\n"
            f"Job ID: {job_id}"
        )

    except TimeoutError as e:
        return (
            f"✗ Timeout: {str(e)}\n"
            f"The job is still processing. Use check_job_status with job_id '{job_id}' "
            f"and endpoint_type 'seedream' to check progress."
        )
    except RuntimeError as e:
        return f"✗ Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in generate_image: {e}", exc_info=True)
        return f"✗ Unexpected error: {str(e)}"


@mcp.tool()
async def edit_image(
    prompt: str,
    image_urls: list[str],
    resolution: Literal["1k", "2k", "4k"] = "2k",
    aspect_ratio: str | None = None,
    output_format: Literal["jpeg", "png"] = "jpeg",
    enable_base64_output: bool = False,
    enable_sync_mode: bool = False,
    max_wait_seconds: int = 300
) -> str:
    """Edit or transform images using Nano Banana Pro Edit API.

    This tool applies AI-powered edits to existing images based on text descriptions.
    You can adjust style, add/remove elements, change backgrounds, enhance quality, etc.

    Args:
        prompt: Description of desired edits or transformations. Be specific about
            what changes you want (e.g., "change background to sunset", "add studio
            lighting", "remove watermark", "enhance colors").
        image_urls: List of 1-10 publicly accessible image URLs to edit.
            Images must be reachable via HTTP/HTTPS. Common formats supported: JPEG, PNG, WebP.
        resolution: Output resolution. Options:
            - "1k": Lower resolution, faster processing ($0.14)
            - "2k": Standard resolution, best value ($0.14) [default]
            - "4k": High resolution for detailed work ($0.24)
        aspect_ratio: Output aspect ratio (optional). If not specified, maintains original.
            Options: "1:1" (square), "16:9" (landscape), "9:16" (portrait), "3:2", "2:3",
            "4:3", "3:4", "4:5", "5:4", "21:9"
        output_format: Output file format. Options:
            - "jpeg": Smaller file size, good for photos (default)
            - "png": Lossless quality, good for graphics
        enable_base64_output: Return base64-encoded image data instead of URL.
            Default: false (return URL)
        enable_sync_mode: Enable synchronous mode for immediate processing.
            Default: false (asynchronous processing)
        max_wait_seconds: Maximum time to wait for job completion in seconds.
            Default: 300 (5 minutes)

    Returns:
        Success message with edited image URL, resolution, cost, and job ID.
        Format: "✓ Image edited successfully!\nURL: ...\nResolution: ...\nCost: $...\nJob ID: ..."

    Examples:
        - "Add dramatic sunset lighting to this portrait"
        - "Remove background and replace with solid white"
        - "Enhance colors and increase sharpness for product photography"
        - "Transform into oil painting style while keeping the subject"
    """
    try:
        # Validate image count
        if len(image_urls) < NANO_BANANA_MIN_IMAGES:
            return (
                f"✗ No images provided. "
                f"You must provide at least {NANO_BANANA_MIN_IMAGES} image URL."
            )

        if len(image_urls) > NANO_BANANA_MAX_IMAGES:
            return (
                f"✗ Too many images ({len(image_urls)}). "
                f"Maximum is {NANO_BANANA_MAX_IMAGES} images."
            )

        # Validate resolution
        if resolution not in NANO_BANANA_RESOLUTIONS:
            valid_opts = ", ".join(
                f"{r} (${NANO_BANANA_PRICING[r]})"
                for r in NANO_BANANA_RESOLUTIONS
            )
            return (
                f"✗ Invalid resolution '{resolution}'. "
                f"Valid options: {valid_opts}"
            )

        # Validate aspect ratio if provided
        if aspect_ratio and aspect_ratio not in NANO_BANANA_ASPECT_RATIOS:
            return (
                f"✗ Invalid aspect_ratio '{aspect_ratio}'. "
                f"Valid options: {', '.join(NANO_BANANA_ASPECT_RATIOS)}"
            )

        # Validate output format
        if output_format not in NANO_BANANA_FORMATS:
            return (
                f"✗ Invalid output_format '{output_format}'. "
                f"Valid options: {', '.join(NANO_BANANA_FORMATS)}"
            )

        logger.info(
            f"Editing image(s): prompt='{prompt[:50]}...', "
            f"images={len(image_urls)}, resolution={resolution}"
        )

        # Prepare job input
        input_data = {
            "prompt": prompt,
            "images": image_urls,  # API expects "images" not "image_urls"
            "resolution": resolution,
            "output_format": output_format,
            "enable_base64_output": enable_base64_output,
            "enable_sync_mode": enable_sync_mode
        }

        # Add optional aspect_ratio if provided
        if aspect_ratio:
            input_data["aspect_ratio"] = aspect_ratio

        # Submit job
        result = await client.submit_job(config.nano_banana_endpoint_id, input_data)
        job_id = result.get("id")

        if not job_id:
            return "✗ Failed to submit job: No job ID returned"

        # Poll for completion
        completed = await client.poll_until_complete(
            config.nano_banana_endpoint_id,
            job_id,
            max_wait_seconds
        )

        # Extract result
        output = completed.get("output", {})
        image_url = output.get("result")
        cost = NANO_BANANA_PRICING.get(resolution, 0.0)

        if not image_url:
            return f"✗ Job completed but no image URL found\nJob ID: {job_id}"

        result_msg = (
            f"✓ Image edited successfully!\n"
            f"URL: {image_url}\n"
            f"Resolution: {resolution}\n"
            f"Cost: ${cost:.2f}\n"
            f"Job ID: {job_id}"
        )

        if aspect_ratio:
            result_msg += f"\nAspect Ratio: {aspect_ratio}"

        return result_msg

    except TimeoutError as e:
        return (
            f"✗ Timeout: {str(e)}\n"
            f"The job is still processing. Use check_job_status with job_id '{job_id}' "
            f"and endpoint_type 'nano_banana' to check progress."
        )
    except RuntimeError as e:
        return f"✗ Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in edit_image: {e}", exc_info=True)
        return f"✗ Unexpected error: {str(e)}"


@mcp.tool()
async def check_job_status(
    job_id: str,
    endpoint_type: Literal["seedream", "nano_banana"]
) -> str:
    """Check the status of a previously submitted job.

    Use this tool to monitor long-running jobs or check on jobs that timed out.
    Works for both image generation (Seedream) and image editing (Nano Banana) jobs.

    Args:
        job_id: Job ID returned from generate_image or edit_image.
            Format: typically a UUID like "abc123-def456"
        endpoint_type: Which API the job was submitted to:
            - "seedream": For text-to-image generation jobs
            - "nano_banana": For image editing jobs

    Returns:
        Current job status with result URL if completed.
        Possible statuses: IN_QUEUE, IN_PROGRESS, COMPLETED, FAILED

    Examples:
        - Check a generation job: check_job_status("abc123-def456", "seedream")
        - Check an editing job: check_job_status("xyz789-ghi012", "nano_banana")
    """
    try:
        # Map endpoint type to endpoint ID
        endpoint_id = (
            config.seedream_endpoint_id
            if endpoint_type == "seedream"
            else config.nano_banana_endpoint_id
        )

        logger.info(f"Checking status: job_id={job_id}, type={endpoint_type}")

        # Get current status
        result = await client.get_status(endpoint_id, job_id)
        status = result.get("status", "UNKNOWN")

        if status == "COMPLETED":
            output = result.get("output", {})
            image_url = output.get("result")

            if not image_url:
                return f"Status: COMPLETED\nJob ID: {job_id}\n⚠ No image URL found in result"

            response = f"Status: COMPLETED\nURL: {image_url}\nJob ID: {job_id}"

            # Add cost for Nano Banana
            if endpoint_type == "nano_banana":
                # Try to extract resolution from output or default to 2k
                resolution = output.get("resolution", "2k")
                cost = NANO_BANANA_PRICING.get(resolution, 0.14)
                response += f"\nCost: ${cost:.2f}"

            # Add seed for Seedream
            if endpoint_type == "seedream":
                seed = output.get("seed")
                if seed is not None:
                    response += f"\nSeed: {seed}"

            return response

        elif status == "FAILED":
            error_msg = result.get("error", "Unknown error")
            if "output" in result and isinstance(result["output"], dict):
                error_msg = result["output"].get("error", error_msg)

            return f"Status: FAILED\nError: {error_msg}\nJob ID: {job_id}"

        elif status in ["IN_QUEUE", "IN_PROGRESS"]:
            return (
                f"Status: {status}\n"
                f"The job is still processing. Check again in a few seconds.\n"
                f"Job ID: {job_id}"
            )

        else:
            return f"Status: {status}\nJob ID: {job_id}"

    except RuntimeError as e:
        return f"✗ Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in check_job_status: {e}", exc_info=True)
        return f"✗ Unexpected error: {str(e)}"


@mcp.tool()
def get_api_info(
    api: Literal["seedream", "nano_banana", "all"] = "all"
) -> str:
    """Get information about supported parameters and capabilities.

    This tool provides reference information about what each API supports,
    including valid parameter values, pricing, and best practices.

    Args:
        api: Which API to get information about:
            - "seedream": Seedream V4 T2I text-to-image generation
            - "nano_banana": Nano Banana Pro Edit image editing
            - "all": Information about both APIs (default)

    Returns:
        Formatted reference information including supported parameters,
        constraints, pricing, and usage recommendations.

    Examples:
        - Get all API info: get_api_info()
        - Get only Seedream info: get_api_info("seedream")
        - Get only Nano Banana info: get_api_info("nano_banana")
    """
    if api == "seedream":
        return SEEDREAM_INFO
    elif api == "nano_banana":
        return NANO_BANANA_INFO
    else:
        return ALL_INFO


def main():
    """Entry point for the MCP server."""
    logger.info("Starting Runpod Image APIs MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
