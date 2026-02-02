# RunPod Image MCP Server

An MCP server that gives **Claude Code** and **Cursor** the ability to generate and edit images using RunPod's Seedream V4 and Nano Banana Pro APIs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager
- A [RunPod](https://runpod.io) API key

## Setup

### Claude Code

**Quick Start (one command):**

```bash
claude mcp add runpod-image-apis \
  -e RUNPOD_API_KEY=your_api_key \
  -- uvx runpod-mcp-server
```

Restart Claude Code and the tools are available.

**Manual setup** (clone and run locally): add to `.mcp.json` (project-level or `~/.claude/.mcp.json` for global):

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

### Cursor

**Quick Start:** create or edit your MCP config and add the server.

- **Project-only:** create `.cursor/mcp.json` in your project root.
- **All projects:** create `~/.cursor/mcp.json` in your home directory.

**If using uvx** (no clone needed):

```json
{
  "mcpServers": {
    "runpod-image-apis": {
      "command": "uvx",
      "args": ["runpod-mcp-server"],
      "env": {
        "RUNPOD_API_KEY": "your_api_key"
      }
    }
  }
}
```

**If running from a cloned repo:**

```bash
git clone https://github.com/jashwanth0712/runpod-image-mcp.git
cd runpod-image-mcp
```

Then use one of the configs below.

In **project** `.cursor/mcp.json` (use `${workspaceFolder}` so it works for any project that contains the clone):

```json
{
  "mcpServers": {
    "runpod-image-apis": {
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}", "runpod-mcp-server"],
      "env": {
        "RUNPOD_API_KEY": "your_api_key"
      }
    }
  }
}
```

In **global** `~/.cursor/mcp.json`, use the absolute path to the repo:

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

Replace `/path/to/runpod-image-mcp` with the actual path. Restart Cursor (or reload the window) so the new MCP server is picked up.

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_image` | Generate images from text prompts (Seedream V4 T2I). Supports sizes up to 4096x4096, negative prompts, and seed control. |
| `edit_image` | Edit/transform existing images (Nano Banana Pro Edit). Accepts 1-10 image URLs with 1k/2k/4k resolution options. |
| `check_job_status` | Check the status of a previously submitted generation or editing job. |
| `get_api_info` | Get reference info about supported parameters, sizes, pricing, and capabilities. |

## Usage Examples

Once configured, ask Claude or Cursor naturally:

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
