#!/usr/bin/env python3
"""Simple HTTP server for Synesthesia with proper CORS headers"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
DIRECTORY = "synesthesia/static"

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for WASM"""
    
    def end_headers(self):
        # Required headers for Pyodide/WASM
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Access-Control-Allow-Origin', '*')
        # Additional headers for proper WASM support
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_GET(self):
        # Serve from the static directory
        self.directory = DIRECTORY
        return super().do_GET()

def main():
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"\n🎨 Synesthesia - GLiNER Mood Chat Client")
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"📁 Serving from: {DIRECTORY}")
        print(f"\n✨ Open your browser to http://localhost:{PORT} to start chatting!")
        print(f"💡 Tip: You'll need a Claude API key from https://console.anthropic.com/")
        print(f"\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Thanks for using Synesthesia!")

if __name__ == "__main__":
    main()