// Synesthesia - GLiNER Mood Chat Application

let pyodide = null;
let analyzer = null;
let apiKey = null;
let messageHistory = [];
let moodTrajectory = [];

// Initialize Pyodide and load the mood analyzer
async function initializePyodide() {
    const statusEl = document.getElementById('processing-indicator');
    statusEl.classList.add('active');
    statusEl.querySelector('.processing-text').textContent = 'Loading WASM runtime...';
    
    try {
        console.log('Starting Pyodide initialization...');
        
        // Check if loadPyodide is available
        if (typeof loadPyodide === 'undefined') {
            throw new Error('loadPyodide is not available. Check if pyodide.js loaded correctly.');
        }
        
        console.log('Loading Pyodide...');
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
        });
        
        console.log('Pyodide loaded, installing packages...');
        // Load required packages
        await pyodide.loadPackage(['numpy']);
        
        console.log('Loading mood analyzer module...');
        // Load our mood analyzer module
        const response = await fetch('py/mood_analyzer.py');
        if (!response.ok) {
            throw new Error(`Failed to fetch mood_analyzer.py: ${response.status}`);
        }
        const code = await response.text();
        
        // Execute the code in the global namespace first
        pyodide.runPython(code);
        
        console.log('Initializing analyzer...');
        // Now create the analyzer (functions should be available globally)
        pyodide.runPython(`
analyzer = create_analyzer()
print("Analyzer created successfully")
        `);
        
        console.log('Pyodide initialized successfully');
        statusEl.classList.remove('active');
        
    } catch (error) {
        console.error('Failed to initialize Pyodide:', error);
        console.error('Error stack:', error.stack);
        statusEl.querySelector('.processing-text').textContent = `Failed to load WASM runtime: ${error.message}`;
        // Keep error visible and don't remove the active class
        statusEl.style.backgroundColor = '#ffebee';
        statusEl.style.color = '#c62828';
        // Also show in alert for visibility
        setTimeout(() => {
            alert(`WASM Runtime Error: ${error.message}\n\nCheck browser console for details.`);
        }, 500);
    }
}

// Claude API integration
class ClaudeChat {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.conversationHistory = [];
    }
    
    async sendMessage(message) {
        this.conversationHistory.push({ role: 'user', content: message });
        
        try {
            const response = await fetch('http://localhost:8001/claude', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey
                },
                body: JSON.stringify({
                    model: 'claude-3-5-sonnet-20241022',
                    messages: this.conversationHistory,
                    max_tokens: 1000
                })
            });
            
            if (!response.ok) {
                const errorData = await response.text();
                console.error('API Response:', response.status, errorData);
                throw new Error(`API error: ${response.status} - ${errorData}`);
            }
            
            const data = await response.json();
            const assistantMessage = data.content[0].text;
            
            this.conversationHistory.push({ role: 'assistant', content: assistantMessage });
            
            return assistantMessage;
            
        } catch (error) {
            console.error('Claude API error:', error);
            // Check if it's a connection error
            if (error.message.includes('Failed to fetch')) {
                return "Connection error: Make sure the API proxy is running (python3 api_proxy.py in another terminal).";
            }
            return `Error: ${error.message}`;
        }
    }
}

// Message handling and display
class MessageHandler {
    constructor() {
        this.wordBuffer = [];
        this.currentMessage = null;
        this.bufferSize = 15;
    }
    
    async processMessage(text, sender = 'user') {
        const message = {
            id: Date.now(),
            sender: sender,
            text: text,
            timestamp: new Date(),
            highlights: [],
            mood: null
        };
        
        // Add to main chat immediately
        this.displayMessage(message);
        
        // Process text in chunks for mood analysis
        const words = text.split(' ');
        let processedText = '';
        
        for (let i = 0; i < words.length; i++) {
            processedText += (i > 0 ? ' ' : '') + words[i];
            this.wordBuffer.push(words[i]);
            
            if (this.wordBuffer.length >= this.bufferSize) {
                await this.analyzeBuffer(message, processedText);
                this.wordBuffer = this.wordBuffer.slice(-5); // Keep last 5 words for context
            }
        }
        
        // Process any remaining words
        if (this.wordBuffer.length > 0) {
            await this.analyzeBuffer(message, text);
        }
        
        messageHistory.push(message);
        return message;
    }
    
    async analyzeBuffer(message, textUpToNow) {
        if (!pyodide) return;
        
        try {
            const result = pyodide.runPython(`
import json
result = analyze_text(analyzer, "${textUpToNow.replace(/"/g, '\\"')}")
result
            `);
            
            const analysis = JSON.parse(result);
            
            if (analysis.highlights) {
                this.updateMessageHighlights(message, analysis);
                this.updateEmotionPanels(message, analysis);
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
        }
    }
    
    displayMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        const messageEl = document.createElement('div');
        messageEl.className = 'message';
        messageEl.id = `message-${message.id}`;
        
        messageEl.innerHTML = `
            <div class="message-header">
                <span class="message-sender">${message.sender === 'user' ? 'You' : 'Claude'}</span>
                <span class="message-time">${message.timestamp.toLocaleTimeString()}</span>
            </div>
            <div class="message-content" id="content-${message.id}">${message.text}</div>
        `;
        
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateMessageHighlights(message, analysis) {
        const contentEl = document.getElementById(`content-${message.id}`);
        if (!contentEl || !analysis.highlights) return;
        
        let highlightedText = message.text;
        const sortedHighlights = analysis.highlights.sort((a, b) => b.start - a.start);
        
        sortedHighlights.forEach(highlight => {
            const before = highlightedText.substring(0, highlight.start);
            const highlighted = highlightedText.substring(highlight.start, highlight.end);
            const after = highlightedText.substring(highlight.end);
            
            highlightedText = `${before}<span class="emotion-highlight" 
                style="background-color: ${highlight.color}40; color: ${highlight.color};" 
                data-emotion="${highlight.label}">${highlighted}</span>${after}`;
        });
        
        contentEl.innerHTML = highlightedText;
        message.highlights = analysis.highlights;
        message.mood = analysis.mood;
    }
    
    updateEmotionPanels(message, analysis) {
        if (!analysis.highlights || analysis.highlights.length === 0) return;
        
        // Add emotional words to appropriate panel based on sender
        const panelId = message.sender === 'user' ? 'cool-messages' : 'warm-messages';
        const panel = document.getElementById(panelId);
        
        analysis.highlights.forEach(highlight => {
            const wordEl = document.createElement('div');
            wordEl.className = 'emotion-word';
            wordEl.style.backgroundColor = highlight.color + '40';
            wordEl.style.color = highlight.color;
            wordEl.style.borderLeftColor = highlight.color;
            wordEl.innerHTML = `
                <span class="word-text">${highlight.text}</span>
                <span class="word-label">${highlight.label}</span>
            `;
            
            panel.appendChild(wordEl);
            panel.scrollTop = panel.scrollHeight;
        });
        
        // Update current mood indicator with dominant emotion
        if (analysis.mood) {
            const moodValue = document.getElementById('current-mood');
            moodValue.textContent = analysis.mood.spectrum.charAt(0).toUpperCase() + analysis.mood.spectrum.slice(1);
            moodValue.style.backgroundColor = analysis.mood.color + '20';
            moodValue.style.color = analysis.mood.color;
        }
    }
    
    updateEntityList(entities) {
        const entityList = document.getElementById('entity-list');
        entityList.innerHTML = '';
        
        entities.forEach(entity => {
            const entityEl = document.createElement('div');
            entityEl.className = 'entity-item';
            
            const color = this.getEntityColor(entity.label);
            entityEl.innerHTML = `
                <div>
                    <span class="entity-label" style="background-color: ${color}"></span>
                    <span>${entity.text} (${entity.label})</span>
                </div>
                <span class="entity-score">${(entity.score * 100).toFixed(0)}%</span>
            `;
            
            entityList.appendChild(entityEl);
        });
    }
    
    getEntityColor(label) {
        const colorMap = {
            'sad': '#4A90E2',
            'happy': '#FADB14',
            'angry': '#F5222D',
            'excited': '#FA8C16',
            'calm': '#52C41A',
            'frustrated': '#FF7A45'
        };
        return colorMap[label] || '#888888';
    }
    
    updateMoodTrajectory(mood) {
        moodTrajectory.push({
            time: Date.now(),
            spectrum: mood.spectrum,
            intensity: mood.intensity,
            color: mood.color
        });
        
        // Keep last 20 points
        if (moodTrajectory.length > 20) {
            moodTrajectory.shift();
        }
        
        this.drawMoodGraph();
    }
    
    drawMoodGraph() {
        const canvas = document.getElementById('mood-graph');
        const ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (moodTrajectory.length < 2) return;
        
        ctx.beginPath();
        ctx.strokeStyle = '#888';
        ctx.lineWidth = 2;
        
        moodTrajectory.forEach((point, i) => {
            const x = (i / (moodTrajectory.length - 1)) * canvas.width;
            const y = canvas.height - (point.intensity * canvas.height);
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }
}

// Initialize the application
const messageHandler = new MessageHandler();
let claudeChat = null;

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Pyodide
    await initializePyodide();
    
    // API key modal handling
    const apiModal = document.getElementById('api-modal');
    const apiKeyInput = document.getElementById('api-key-input');
    const apiKeySubmit = document.getElementById('api-key-submit');
    
    // Check for stored API key
    const storedKey = localStorage.getItem('claude-api-key');
    if (storedKey) {
        apiKey = storedKey;
        claudeChat = new ClaudeChat(apiKey);
    } else {
        apiModal.classList.add('active');
    }
    
    apiKeySubmit.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            apiKey = key;
            localStorage.setItem('claude-api-key', key);
            claudeChat = new ClaudeChat(apiKey);
            apiModal.classList.remove('active');
        }
    });
    
    // Chat input handling
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const wordCount = document.getElementById('word-count');
    
    chatInput.addEventListener('input', () => {
        const words = chatInput.value.trim().split(/\s+/).filter(w => w.length > 0);
        wordCount.textContent = `${words.length} words`;
    });
    
    const sendMessage = async () => {
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Clear input
        chatInput.value = '';
        wordCount.textContent = '0 words';
        
        // Process user message
        await messageHandler.processMessage(text, 'user');
        
        // Get Claude's response
        if (claudeChat) {
            const processingEl = document.getElementById('processing-indicator');
            processingEl.classList.add('active');
            processingEl.querySelector('.processing-text').textContent = 'Claude is thinking...';
            
            const response = await claudeChat.sendMessage(text);
            
            processingEl.classList.remove('active');
            
            // Process Claude's response
            await messageHandler.processMessage(response, 'assistant');
        }
    };
    
    sendBtn.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Remove welcome message on first message
    let welcomeRemoved = false;
    const originalProcessMessage = messageHandler.processMessage.bind(messageHandler);
    messageHandler.processMessage = async function(...args) {
        if (!welcomeRemoved) {
            const welcomeMsg = document.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
                welcomeRemoved = true;
            }
        }
        return originalProcessMessage(...args);
    };
});

// Export for debugging
window.synesthesia = {
    pyodide,
    messageHandler,
    claudeChat,
    messageHistory,
    moodTrajectory
};