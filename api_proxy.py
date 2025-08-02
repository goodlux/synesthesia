#!/usr/bin/env python3
"""Simple proxy server for Claude API to handle CORS"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse
import ssl

PORT = 8001

class APIProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key')
        self.end_headers()
    
    def do_POST(self):
        """Proxy POST requests to Claude API"""
        if self.path != '/claude':
            self.send_error(404)
            return
            
        # Read request body
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)
        
        # Get API key from header
        api_key = self.headers.get('x-api-key')
        if not api_key:
            self.send_error(401, 'Missing API key')
            return
        
        # Forward to Claude API
        try:
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=request_body,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            
            # Create SSL context to handle certificates
            ssl_context = ssl.create_default_context()
            
            with urllib.request.urlopen(req, context=ssl_context) as response:
                response_data = response.read()
                
                # Send response back to client
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(error_body.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))

def main():
    server = HTTPServer(('localhost', PORT), APIProxyHandler)
    print(f"\n🔗 Claude API Proxy Server")
    print(f"🚀 Running on http://localhost:{PORT}")
    print(f"📡 Proxying requests to Claude API")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Proxy server stopped")

if __name__ == '__main__':
    main()