# RunPod Image MCP Server

An MCP server that gives Claude Code the ability to generate and edit images using RunPod's Seedream V4 and Nano Banana Pro APIs.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A [RunPod](https://runpod.io) API key and serverless endpoint IDs for Seedream V4 T2I and Nano Banana Pro Edit

## Installation

```bash
git clone https://github.com/jashwanth0712/runpod-image-mcp.git
cd runpod-image-mcp

uv venv
source .venv/bin/activate
uv pip install -e .
```

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

```env
RUNPOD_API_KEY=your_api_key
RUNPOD_SEEDREAM_ENDPOINT_ID=your_seedream_endpoint_id
RUNPOD_NANO_BANANA_ENDPOINT_ID=your_nano_banana_endpoint_id
```

## Claude Code Configuration

Add this to your project's `.mcp.json` (or `~/.claude/.mcp.json` for global config):

```json
{
  "mcpServers": {
    "runpod-image-apis": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/runpod-image-mcp",
      "env": {
        "RUNPOD_API_KEY": "your_api_key",
        "RUNPOD_SEEDREAM_ENDPOINT_ID": "your_seedream_endpoint_id",
        "RUNPOD_NANO_BANANA_ENDPOINT_ID": "your_nano_banana_endpoint_id"
      }
    }
  }
}
```

Replace `/path/to/runpod-image-mcp` with the absolute path to this repo on your machine.

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_image` | Generate images from text prompts (Seedream V4 T2I). Supports custom sizes up to 4096x4096, negative prompts, and seed control. |
| `edit_image` | Edit/transform existing images (Nano Banana Pro Edit). Accepts 1-10 image URLs with 1k/2k/4k resolution options. |
| `check_job_status` | Check the status of a previously submitted generation or editing job. |
| `get_api_info` | Get reference info about supported parameters, sizes, pricing, and capabilities. |

## Usage Examples

Once configured, just ask Claude naturally:

```
Generate a photorealistic sunset over snow-capped mountains with dramatic clouds
```

```
Edit this product photo to have a white background and studio lighting: https://example.com/photo.jpg
```

```
Check the status of job abc123-def456 from Seedream
```

```
What sizes does the Seedream API support?
```

## Troubleshooting

- **Server won't start** -- Verify your `RUNPOD_API_KEY` and endpoint IDs are correct in `.env` or `.mcp.json`.
- **Job timeouts** -- Increase `max_wait_seconds` or use `check_job_status` to poll manually. Large images take longer.
- **No image URL in response** -- Check the RunPod console for job details and endpoint health.

## License

MIT
