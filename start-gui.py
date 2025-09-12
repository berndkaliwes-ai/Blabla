#!/usr/bin/env python3
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path("frontend/dist")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

print("🚀 XTTS V2 Voice Cloning Studio")
print("=" * 50)
print(f"📁 Serving from: {DIRECTORY.absolute()}")
print(f"🌐 Server starting on: http://0.0.0.0:{PORT}")
print("=" * 50)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"✅ GUI is now running at: http://0.0.0.0:{PORT}")
    print("🎉 Open this URL in your browser to see the interface!")
    print("\nPress Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")