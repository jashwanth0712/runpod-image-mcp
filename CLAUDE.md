# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

```bash
# Use uv for package management
uv venv
source .venv/bin/activate

# Install in editable mode
uv pip install -e .
```

## Running/Testing

```bash
# Run the server locally
RUNPOD_API_KEY=your_key uv run runpod-mcp-server

# Test (when implemented)
pytest
```

## Publishing

```bash
uv build
uv publish
```

## RunPod API Integration

**Endpoint IDs** (hardcoded in constants.py):
- Seedream V4 T2I: `seedream-v4-t2i`
- Nano Banana Pro Edit: `nano-banana-pro-edit`

**Async Job Flow**:
1. Submit job to `/v2/{endpoint_id}/run` → get job_id
2. Poll `/v2/{endpoint_id}/status/{job_id}` with exponential backoff (2s, 4s, 8s, then 15s intervals)
3. Extract result URL from completed job output

**Required Environment Variable**:
- `RUNPOD_API_KEY` - Get from https://runpod.io/console/user/settings

## Architecture

**server.py**: FastMCP server with 4 tools (`generate_image`, `edit_image`, `check_job_status`, `get_api_info`). All validation happens here before calling the client. Tools return user-friendly strings (✓/✗ prefixed), never raise exceptions.

**runpod_client.py**: Async HTTP client handling all RunPod API calls. Raises `RuntimeError` for API/network errors, `TimeoutError` for polling timeouts.

**config.py**: Pydantic settings loading `RUNPOD_API_KEY` from env vars or .env file (with `RUNPOD_` prefix).

**constants.py**: API constraints (Seedream: 1024-4096px, Nano Banana: 1k/2k/4k resolutions), pricing, and reference info.
