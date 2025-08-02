# GLiNER Mood Chat Client Specification

## Overview
A real-time chat interface that uses GLiNER (Generalist Named Entity Recognition) to analyze emotional content and visualize mood through color-coded highlighting and spatial positioning.

## Core Concept
**Three-panel layout** with mood-based positioning and real-time emotional entity highlighting:
- **Left Panel**: Messages with cool spectrum emotions (blues/greens)
- **Center Panel**: Shared chat log with highlighted entities
- **Right Panel**: Messages with warm spectrum emotions (reds/oranges)

*Note: Either user or Claude messages can appear in left or right panels - positioning is determined entirely by the emotional content detected by GLiNER, not by sender.*

## Visual Design

### Layout Structure
```
┌─────────────┬─────────────┬─────────────┐
│    COOL     │    CHAT     │    WARM     │
│ (Blue/Green)│   (Shared)  │ (Red/Orange)│
│             │             │             │
│ Calm/Mellow │ Full convo  │ Intense/Hot │
│   messages  │ w/highlights│  messages   │
│ (any sender)│             │ (any sender)│
└─────────────┴─────────────┴─────────────┘
```

### Color Spectrum Mapping
- **Red Zone** (Right): Angry, passionate, excited, aggressive, intense
- **Orange Zone**: Enthusiastic, energetic, urgent, frustrated
- **Yellow Zone**: Happy, optimistic, cheerful, surprised
- **Green Zone**: Calm, content, balanced, hopeful
- **Blue Zone** (Left): Mellow, sad, thoughtful, peaceful, melancholy
- **Purple Zone**: Mysterious, romantic, dreamy, nostalgic

## Technical Implementation

### GLiNER Integration
- **Model**: Standard GLiNER model (pre-trained)
- **Custom Labels**: Define emotion/mood categories for GLiNER to detect:
  - Emotional states: `happy`, `angry`, `sad`, `excited`, `calm`, `frustrated`, `anxious`, `joyful`
  - Intensity modifiers: `very`, `extremely`, `slightly`, `somewhat`, `really`, `quite`
  - Emotional triggers: `love`, `hate`, `fear`, `hope`, `worry`, `stress`, `relief`

### Processing Pipeline
1. **Input Buffering**: Collect 10-20 words before processing
2. **Entity Extraction**: Run GLiNER on word buffer + context
3. **Mood Scoring**: Calculate emotional valence and intensity
4. **Visualization**: Apply highlighting and positioning

### Performance Targets
- **Processing Delay**: 10-20 words (as specified)
- **Analysis Window**: Current message + previous 2-3 messages for context
- **Update Frequency**: Real-time highlighting as analysis completes
- **Target Latency**: <500ms from buffer trigger to highlight

## Features

### Real-time Highlighting
- **Entity Spans**: Highlight detected emotional words/phrases
- **Color Coding**: Match entity type to spectrum position
- **Fade Animation**: Smooth appearance of highlights (300ms transition)
- **Intensity Mapping**: Opacity/saturation based on confidence scores

### Spatial Positioning
- **Content-Based Sorting**: Messages flow to appropriate panel based on dominant emotional tone detected by GLiNER
- **Dynamic Assignment**: Both user and Claude messages can appear in either left (cool) or right (warm) panels
- **Gradient Positioning**: Vertical position within panel reflects emotional intensity
- **Animation**: Smooth movement between panels as conversation mood shifts

### Side Panel Information
- **Entity List**: Live updating list of detected emotions
- **Confidence Scores**: Show GLiNER confidence levels
- **Mood Trajectory**: Simple line graph of conversation mood over time
- **Statistics**: Emotion frequency counts

## User Experience

### Chat Flow
1. User types message in center input
2. Message appears immediately in chat log
3. After 10-20 words, GLiNER processes buffer
4. Emotional entities highlight with color-coded spans
5. Message copies to appropriate side panel (left for cool emotions, right for warm emotions) regardless of sender
6. Side panel updates with new entity detections

### Visual Feedback
- **Typing Indicators**: Show when GLiNER is processing
- **Confidence Visualization**: Border thickness/glow indicates certainty
- **Mood Transitions**: Smooth color transitions for ambiguous emotions

## Technical Stack

### Frontend
- **Framework**: Vanilla JS or React for rapid prototyping
- **WASM**: ONNX.js for GLiNER model inference
- **Styling**: CSS animations for smooth transitions
- **Layout**: CSS Grid for three-panel structure

### Model Requirements
- **GLiNER Model**: Standard pre-trained model with custom label prompting
- **Format**: ONNX export for browser compatibility
- **Size**: Standard GLiNER model size
- **Labels**: Runtime-defined emotion categories passed to model

### Data Flow
```
User Input → Claude API → Response → Buffer (10-20 words) → GLiNER → 
Entity Extraction → Mood Calculation → Color Mapping → UI Update → Panel Positioning
```

## Implementation Timeline (30-minute prototype)

### Phase 1 (10 mins): Basic Layout
- Three-panel CSS grid
- Real chat interface with Claude API integration
- Basic color spectrum CSS classes

### Phase 2 (10 mins): GLiNER Integration
- Real GLiNER model with ONNX.js
- Text highlighting with colored spans
- Live Claude conversation processing

### Phase 3 (10 mins): Polish
- Smooth transitions and animations
- Side panel entity list
- Color spectrum refinement

## Future Enhancements (Post-Prototype)
- Multi-user support with color coding
- Voice input with tone analysis
- Export mood reports
- Additional emotion label experimentation
- Mood history persistence

## Success Metrics
- **Visual Impact**: Clear emotional differentiation between panels for real Claude responses
- **Responsiveness**: Smooth highlighting without UI lag during live conversation
- **Accuracy**: Real-time mood detection on actual Claude conversation
- **Polish**: Professional-looking color transitions and layout
- **Conversation Quality**: Natural chat flow with Claude while mood analysis runs

This spec balances ambitious vision with 30-minute feasibility by using mock data initially while establishing the full interaction pattern.