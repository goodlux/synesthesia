"""Mood analysis using GLiNER for emotional entity recognition"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class EmotionalEntity:
    text: str
    label: str
    start: int
    end: int
    score: float


class MoodAnalyzer:
    """Analyzes text for emotional content using GLiNER"""
    
    # Emotion categories with their color mappings
    EMOTION_COLORS = {
        # Cool spectrum - blues, greens, purples
        "melancholy": {"color": "#5C7CFA", "spectrum": "cool", "intensity": 0.8},
        "pensive": {"color": "#13C2C2", "spectrum": "cool", "intensity": 0.6},
        "serene": {"color": "#48C9B0", "spectrum": "cool", "intensity": 0.3},
        "anxious": {"color": "#722ED1", "spectrum": "cool", "intensity": 0.7},
        
        # Warm spectrum - reds, oranges, yellows
        "fierce": {"color": "#F5222D", "spectrum": "warm", "intensity": 1.0},
        "passionate": {"color": "#FA541C", "spectrum": "warm", "intensity": 0.9},
        "excited": {"color": "#FA8C16", "spectrum": "warm", "intensity": 0.8},
        "agitated": {"color": "#FF7A45", "spectrum": "warm", "intensity": 0.7},
        
        # Neutral/balanced - yellows, light greens
        "joyful": {"color": "#FADB14", "spectrum": "neutral", "intensity": 0.6},
        "content": {"color": "#A0D911", "spectrum": "neutral", "intensity": 0.4},
        "hopeful": {"color": "#52C41A", "spectrum": "neutral", "intensity": 0.5},
        "curious": {"color": "#FFC53D", "spectrum": "neutral", "intensity": 0.5},
    }
    
    # Labels for GLiNER (matches our emotion categories)
    EMOTION_LABELS = [
        "joyful", "melancholy", "fierce", "excited", "pensive", "serene",
        "agitated", "passionate", "hopeful", "anxious", "content", "curious"
    ]
    
    INTENSITY_MODIFIERS = ["very", "extremely", "slightly", "somewhat", "really", "quite"]
    EMOTIONAL_TRIGGERS = ["love", "hate", "fear", "hope", "worry", "stress", "relief"]
    
    def __init__(self):
        self.gliner_model = None
        self.word_buffer = []
        self.buffer_size = 15  # Process after 15 words
        
    async def initialize_model(self):
        """Initialize GLiNER model for WASM environment"""
        # In WASM, we'll use a lightweight version or mock for prototype
        # For now, we'll implement pattern matching as fallback
        self.initialized = True
        
    def add_to_buffer(self, text: str) -> Optional[List[EmotionalEntity]]:
        """Add text to buffer and process if threshold reached"""
        words = text.split()
        self.word_buffer.extend(words)
        
        if len(self.word_buffer) >= self.buffer_size:
            entities = self.process_buffer()
            self.word_buffer = self.word_buffer[-5:]  # Keep last 5 words for context
            return entities
        return None
        
    def process_buffer(self) -> List[EmotionalEntity]:
        """Process the word buffer for emotional entities"""
        text = " ".join(self.word_buffer)
        
        # For prototype: simple pattern matching
        # In production: use actual GLiNER model
        entities = self._mock_entity_extraction(text)
        
        return entities
        
    def _mock_entity_extraction(self, text: str) -> List[EmotionalEntity]:
        """Mock entity extraction for prototype"""
        entities = []
        text_lower = text.lower()
        
        # Sophisticated emotion categorization with trigger words
        emotion_keywords = {
            "joyful": ["happy", "joy", "joyful", "glad", "delighted", "cheerful", "elated", "euphoric", "bliss", "gleeful"],
            "melancholy": ["sad", "unhappy", "depressed", "down", "blue", "gloomy", "somber", "sorrowful", "dejected", "despondent"],
            "fierce": ["angry", "mad", "furious", "rage", "livid", "irate", "wrathful", "incensed", "outraged"],
            "excited": ["excited", "thrilled", "pumped", "energetic", "enthusiastic", "exhilarated", "animated", "vibrant"],
            "pensive": ["thoughtful", "contemplative", "reflective", "introspective", "meditative", "pondering", "wondering"],
            "serene": ["calm", "peaceful", "serene", "relaxed", "tranquil", "placid", "still", "quiet", "zen"],
            "agitated": ["frustrated", "annoyed", "irritated", "agitated", "restless", "tense", "stressed", "bothered"],
            "passionate": ["passionate", "intense", "fervent", "ardent", "zealous", "devoted", "burning", "fiery"],
            "hopeful": ["hopeful", "optimistic", "positive", "confident", "encouraged", "upbeat", "bright"],
            "anxious": ["worried", "anxious", "nervous", "uneasy", "concerned", "apprehensive", "troubled", "distressed"],
            "content": ["content", "satisfied", "pleased", "comfortable", "at ease", "settled", "fulfilled"],
            "curious": ["curious", "interested", "intrigued", "fascinated", "wondering", "questioning", "exploring"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    start = text_lower.find(keyword)
                    entities.append(EmotionalEntity(
                        text=keyword,
                        label=emotion,
                        start=start,
                        end=start + len(keyword),
                        score=0.85
                    ))
                    
        return entities
        
    def calculate_dominant_mood(self, entities: List[EmotionalEntity]) -> Dict:
        """Calculate the dominant mood from detected entities"""
        if not entities:
            return {"spectrum": "neutral", "intensity": 0.5, "color": "#888888"}
            
        # Aggregate scores by spectrum
        spectrum_scores = {"cool": 0, "warm": 0, "neutral": 0}
        total_intensity = 0
        
        for entity in entities:
            if entity.label in self.EMOTION_COLORS:
                emotion_data = self.EMOTION_COLORS[entity.label]
                spectrum_scores[emotion_data["spectrum"]] += entity.score
                total_intensity += emotion_data["intensity"] * entity.score
                
        # Determine dominant spectrum
        dominant_spectrum = max(spectrum_scores, key=spectrum_scores.get)
        avg_intensity = total_intensity / len(entities) if entities else 0.5
        
        # Get representative color
        spectrum_emotions = [
            (label, data) for label, data in self.EMOTION_COLORS.items() 
            if data["spectrum"] == dominant_spectrum
        ]
        if spectrum_emotions:
            color = spectrum_emotions[0][1]["color"]
        else:
            color = "#888888"
            
        return {
            "spectrum": dominant_spectrum,
            "intensity": avg_intensity,
            "color": color,
            "confidence": sum(e.score for e in entities) / len(entities)
        }
        
    def format_for_ui(self, text: str, entities: List[EmotionalEntity], mood: Dict) -> Dict:
        """Format analysis results for UI consumption"""
        # Create highlighted spans
        highlights = []
        for entity in entities:
            if entity.label in self.EMOTION_COLORS:
                highlights.append({
                    "start": entity.start,
                    "end": entity.end,
                    "text": entity.text,
                    "label": entity.label,
                    "color": self.EMOTION_COLORS[entity.label]["color"],
                    "score": entity.score
                })
                
        return {
            "text": text,
            "highlights": highlights,
            "mood": mood,
            "entities": [
                {
                    "text": e.text,
                    "label": e.label,
                    "score": e.score
                } for e in entities
            ]
        }


# WASM-compatible exports
def create_analyzer():
    """Create a new mood analyzer instance"""
    return MoodAnalyzer()


def analyze_text(analyzer: MoodAnalyzer, text: str) -> str:
    """Analyze text and return JSON results"""
    entities = analyzer.add_to_buffer(text)
    
    if entities:
        mood = analyzer.calculate_dominant_mood(entities)
        result = analyzer.format_for_ui(text, entities, mood)
        return json.dumps(result)
    
    return json.dumps({"status": "buffering", "buffer_size": len(analyzer.word_buffer)})