# Synesthesia - GLiNER Mood Chat Client

A real-time chat interface that uses GLiNER (Generalist Named Entity Recognition) to analyze emotional content and visualize mood through color-coded highlighting and spatial positioning.

## Features

- **Three-Panel Layout**: Messages flow to cool (left) or warm (right) panels based on emotional content
- **Real-time Analysis**: Processes text in 15-word buffers using GLiNER in WASM
- **Emotional Highlighting**: Color-coded entity highlighting based on detected emotions
- **Claude Integration**: Chat with Claude while seeing emotional analysis in real-time
- **Mood Trajectory**: Visual graph showing conversation mood over time

## Quick Start

1. Install dependencies with uv:
```bash
uv sync
```

2. Build the WASM files:
```bash
python3 build_wasm.py
```

3. Start BOTH servers in separate terminals:

**Terminal 1 - API Proxy (required for Claude):**
```bash
python3 api_proxy.py
```

**Terminal 2 - Web Server:**
```bash
python3 run_server.py
```

4. Open http://localhost:8000 in your browser

5. Enter your Claude API key when prompted

## Architecture

- **Python/WASM Backend**: GLiNER mood analysis runs in Pyodide
- **JavaScript Frontend**: Real-time UI updates and Claude API integration
- **Three-Panel System**: Automatic emotion-based message positioning

## Emotion Spectrum

- **Cool (Left Panel)**: Sad, melancholy, peaceful, calm, thoughtful
- **Warm (Right Panel)**: Angry, passionate, excited, frustrated, enthusiastic
- **Neutral (Center)**: Happy, content, hopeful

## Development

The project uses `pyproject.toml` for Python dependencies and runs entirely in the browser using Pyodide/WASM.

For development:
```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Format code
black synesthesia/

# Lint
ruff synesthesia/
```