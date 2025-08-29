#!/usr/bin/env python3
"""
Simple static file server for GrowFi Investment Project
Serves your original Django HTML templates and static files
No complex dependencies needed
"""
import os
import http.server
import socketserver
from urllib.parse import urlparse

class GrowFiStaticHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"📄 Request: {path}")
        
        # Route mapping for your investment project
        if path == '/' or path == '/home':
            self.serve_file('myproject/templates/myproject/dashboard.html')
        elif path == '/login':
            self.serve_file('myproject/templates/myproject/login.html')
        elif path == '/register':
            self.serve_file('myproject/templates/myproject/register.html')
        elif path == '/dashboard':
            self.serve_file('myproject/templates/myproject/dashboard.html')
        elif path == '/investment_plans':
            self.serve_file('myproject/templates/myproject/investment_plans.html')
        elif path == '/my_investments':
            self.serve_file('myproject/templates/myproject/my_investments.html')
        elif path.startswith('/static/'):
            # Serve static files (CSS, JS, images)
            file_path = path[1:]  # Remove leading slash
            if os.path.exists(file_path):
                self.serve_file(file_path)
            else:
                self.send_error(404, f"Static file not found: {file_path}")
        else:
            # Try to serve other template files
            template_path = f"myproject/templates/myproject{path}.html"
            if os.path.exists(template_path):
                self.serve_file(template_path)
            else:
                # Default to dashboard
                self.serve_file('myproject/templates/myproject/dashboard.html')
    
    def serve_file(self, file_path):
        try:
            if os.path.exists(file_path):
                # Determine content type
                if file_path.endswith('.html'):
                    content_type = 'text/html; charset=utf-8'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    content_type = 'image/*'
                else:
                    content_type = 'text/plain'
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                
                print(f"✅ Served: {file_path}")
            else:
                print(f"❌ File not found: {file_path}")
                self.send_error(404, f"File not found: {file_path}")
        except Exception as e:
            print(f"💥 Error serving {file_path}: {e}")
            self.send_error(500, f"Error serving file: {str(e)}")

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Starting GrowFi Investment Platform")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🌐 Port: {port}")
    
    # List available templates
    template_dir = "myproject/templates/myproject"
    if os.path.exists(template_dir):
        templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        print(f"📋 Available templates: {len(templates)}")
        for template in templates[:5]:  # Show first 5
            print(f"   - {template}")
        if len(templates) > 5:
            print(f"   ... and {len(templates) - 5} more")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), GrowFiStaticHandler) as httpd:
            print(f"🎯 Server running at http://0.0.0.0:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
