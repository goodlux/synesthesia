# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Synesthesia is a GLiNER Mood Chat Client that creates a real-time chat interface with emotional content analysis and visualization. The project uses GLiNER (Generalist Named Entity Recognition) to analyze emotional content in chat messages and visualize mood through color-coded highlighting and spatial positioning.

## Key Architecture

### Three-Panel Layout System
- **Left Panel**: Cool spectrum emotions (blues/greens) - messages with calm, mellow, peaceful, or sad emotional content
- **Center Panel**: Shared chat log with highlighted emotional entities
- **Right Panel**: Warm spectrum emotions (reds/oranges) - messages with intense, passionate, excited, or angry emotional content

Messages from either user or Claude can appear in any panel based on their emotional content, not sender identity.

### GLiNER Integration
- Uses standard pre-trained GLiNER model with custom emotion labels
- Processes text in 10-20 word buffers for real-time analysis
- Detects emotional states, intensity modifiers, and emotional triggers
- ONNX.js for browser-based inference

### Color Spectrum Mapping
- Red: Angry, passionate, excited, aggressive, intense
- Orange: Enthusiastic, energetic, urgent, frustrated
- Yellow: Happy, optimistic, cheerful, surprised
- Green: Calm, content, balanced, hopeful
- Blue: Mellow, sad, thoughtful, peaceful, melancholy
- Purple: Mysterious, romantic, dreamy, nostalgic

## Development Commands

Since this is a new project without established tooling, typical commands will depend on the implementation approach chosen:

### For Vanilla JS Implementation
```bash
# Serve static files locally
python -m http.server 8000
# or
npx serve .
```

### For React-based Implementation
```bash
# Initialize project (if not already done)
npm init -y
npm install react react-dom

# Development server
npm run dev

# Build for production
npm run build
```

### GLiNER Model Setup
```bash
# Convert GLiNER model to ONNX format (if needed)
python convert_to_onnx.py

# Serve model files with appropriate CORS headers
python -m http.server --bind localhost 8000
```

## Technical Implementation Notes

### Data Flow
1. User input → Claude API → Response
2. Buffer accumulates 10-20 words
3. GLiNER processes buffer for entity extraction
4. Mood calculation based on detected entities
5. Color mapping and UI updates
6. Panel positioning based on dominant emotional tone

### Performance Targets
- Processing delay: 10-20 words (as specified)
- Target latency: <500ms from buffer trigger to highlight
- Smooth animations: 300ms transitions

### Key Files to Create
- `index.html`: Main layout structure with three-panel grid
- `chat.js`: Claude API integration and message handling
- `gliner.js`: GLiNER model loading and inference
- `mood-analyzer.js`: Entity extraction to mood mapping logic
- `ui.js`: Highlighting, animations, and panel management
- `styles.css`: Color spectrum definitions and transitions