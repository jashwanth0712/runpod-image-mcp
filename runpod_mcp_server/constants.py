"""Constants and validation rules for Runpod APIs."""

# Endpoint IDs (fixed RunPod serverless endpoint slugs)
SEEDREAM_ENDPOINT_ID = "seedream-v4-t2i"
NANO_BANANA_ENDPOINT_ID = "nano-banana-pro-edit"

# Seedream V4 T2I
SEEDREAM_MIN_SIZE = 1024
SEEDREAM_MAX_SIZE = 4096
SEEDREAM_DEFAULT_SIZE = "2048*2048"

# Nano Banana Pro Edit
NANO_BANANA_RESOLUTIONS = ["1k", "2k", "4k"]
NANO_BANANA_ASPECT_RATIOS = [
    "1:1", "3:2", "2:3", "4:3", "3:4",
    "4:5", "5:4", "16:9", "9:16", "21:9"
]
NANO_BANANA_FORMATS = ["jpeg", "png"]
NANO_BANANA_MIN_IMAGES = 1
NANO_BANANA_MAX_IMAGES = 10

# Pricing
NANO_BANANA_PRICING = {
    "1k": 0.14,
    "2k": 0.14,
    "4k": 0.24
}

# API Information
SEEDREAM_INFO = """## Seedream V4 T2I (Text-to-Image Generation)

**Supported Sizes:**
- Range: 1024×1024 to 4096×4096 pixels
- Format: "width*height" (e.g., "2048*2048")
- Default: 2048×2048
- Common options: "1024*1024", "2048*2048", "3072*3072", "4096*4096"

**Features:**
- Negative prompts: Exclude unwanted elements
- Seed control: Use -1 for random, or specific number for reproducibility
- Safety checker: Content filtering enabled by default
- High quality photorealistic and artistic outputs

**Best Practices:**
- Use detailed prompts for better results
- Larger sizes take longer to generate
- Use negative prompts to avoid common issues
- Save seed values to reproduce favorite results
"""

NANO_BANANA_INFO = """## Nano Banana Pro Edit (Image Editing)

**Supported Resolutions:**
- 1k: $0.14 per image
- 2k: $0.14 per image (default)
- 4k: $0.24 per image

**Aspect Ratios:**
- Square: 1:1
- Landscape: 3:2, 4:3, 16:9, 21:9
- Portrait: 2:3, 3:4, 9:16
- Social: 4:5 (Instagram), 5:4

**Input Requirements:**
- 1-10 publicly accessible image URLs
- Images must be reachable via HTTP/HTTPS
- Supports common formats (JPEG, PNG, WebP)

**Output Options:**
- Formats: JPEG (smaller, faster) or PNG (lossless)
- Base64 output: Optional for inline embedding
- Resolution affects quality and cost

**Best Practices:**
- Use 2k for most editing tasks (best value)
- Use 4k only when high detail is required
- Provide clear, specific editing instructions
- Aspect ratio affects composition significantly
"""

ALL_INFO = f"""{SEEDREAM_INFO}

{NANO_BANANA_INFO}

**Tips:**
- Both APIs process jobs asynchronously
- Use check_job_status to monitor long-running jobs
- Jobs typically complete in 30-90 seconds
- Timeouts default to 300 seconds (5 minutes)
"""
