#!/bin/bash

echo "🎨 Setting up Synesthesia..."

# Install dependencies with uv
echo "📦 Installing dependencies with uv..."
uv sync

# Build WASM files
echo "🔨 Building WASM files..."
python3 build_wasm.py

echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  python3 run_server.py"
echo ""
echo "Then open http://localhost:8000 in your browser"