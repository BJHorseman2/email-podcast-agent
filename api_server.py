#!/usr/bin/env python3
"""
Simple API server for the HTML UI
Handles podcast processing requests
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import subprocess
import threading
import os

class PodcastAPIHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests from the UI"""
        if self.path == '/api/process/mando':
            self.process_mando()
        elif self.path == '/api/process/puck':
            self.process_puck()
        else:
            self.send_error(404)
    
    def process_mando(self):
        """Process Mando Minutes request"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Start processing in background
        def run_mando():
            try:
                result = subprocess.run(
                    ["python3", "send_clean_mando.py"],
                    capture_output=True,
                    text=True
                )
                # Log result
                print(f"Mando processing result: {result.returncode}")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"Errors: {result.stderr}")
            except Exception as e:
                print(f"Error processing Mando: {e}")
        
        thread = threading.Thread(target=run_mando)
        thread.start()
        
        # Send immediate response
        response = {"status": "processing", "message": "Mando Minutes processing started"}
        self.wfile.write(json.dumps(response).encode())
    
    def process_puck(self):
        """Process Puck News request"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"status": "unavailable", "message": "Puck News processing coming soon"}
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    """Run the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, PodcastAPIHandler)
    
    print(f"🌐 Email-to-Podcast Web Server")
    print(f"=" * 40)
    print(f"Server running at: http://localhost:{port}")
    print(f"UI available at: http://localhost:{port}/simple.html")
    print(f"")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 40)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")

if __name__ == "__main__":
    run_server()
