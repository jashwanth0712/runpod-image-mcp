# RunPod Image MCP Server

An MCP server that gives Claude Code the ability to generate and edit images using RunPod's Seedream V4 and Nano Banana Pro APIs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager
- A [RunPod](https://runpod.io) API key

## Quick Start (One Command)

Add the MCP server to Claude Code directly:

```bash
claude mcp add runpod-image-apis \
  -e RUNPOD_API_KEY=your_api_key \
  -- uvx runpod-mcp-server
```

That's it. Restart Claude Code and the tools are available.

## Manual Setup

If you prefer to clone and run locally:

```bash
git clone https://github.com/jashwanth0712/runpod-image-mcp.git
cd runpod-image-mcp
```

Then add to your `.mcp.json` (project-level or `~/.claude/.mcp.json` for global):

```json
{
  "mcpServers": {
    "runpod-image-apis": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/runpod-image-mcp", "runpod-mcp-server"],
      "env": {
        "RUNPOD_API_KEY": "your_api_key"
      }
    }
  }
}
```

Replace `/path/to/runpod-image-mcp` with the absolute path to the cloned repo.

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_image` | Generate images from text prompts (Seedream V4 T2I). Supports sizes up to 4096x4096, negative prompts, and seed control. |
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

- **Server won't start** -- Verify your `RUNPOD_API_KEY` is correct.
- **Job timeouts** -- Increase `max_wait_seconds` or use `check_job_status` to poll manually. Large images take longer.
- **No image URL in response** -- Check the RunPod console for job details and endpoint health.

## License

MIT
