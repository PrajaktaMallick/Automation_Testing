#!/usr/bin/env python3
"""
Simple test server to verify the setup
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TestRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        print(f"GET request received: {self.path}")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": "Test server is working!",
                "status": "running",
                "path": self.path
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "server": "test-server"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_test_server():
    """Run the test server"""
    port = 8001  # Try a different port
    server_address = ('localhost', port)

    try:
        httpd = HTTPServer(server_address, TestRequestHandler)
        print("🚀 Starting Test Server")
        print(f"📡 Server running on http://localhost:{port}")
        print("✅ Ready to test!")
        print()

        httpd.serve_forever()
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        print("🔄 Trying different port...")

        # Try port 8002
        port = 8002
        server_address = ('localhost', port)
        httpd = HTTPServer(server_address, TestRequestHandler)
        print(f"📡 Server running on http://localhost:{port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_test_server()
