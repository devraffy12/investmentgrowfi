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
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process Django template syntax for HTML files
                if file_path.endswith('.html'):
                    content = self.process_django_template(content)
                
                content_bytes = content.encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content_bytes))
                self.end_headers()
                self.wfile.write(content_bytes)
                
                print(f"✅ Served: {file_path}")
            else:
                print(f"❌ File not found: {file_path}")
                self.send_error(404, f"File not found: {file_path}")
        except Exception as e:
            print(f"💥 Error serving {file_path}: {e}")
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def process_django_template(self, content):
        """Process Django template syntax and replace with actual values"""
        import re
        
        # Sample user data for demo
        user_data = {
            'first_name': 'John',
            'last_name': 'Investor',
            'phone_number': '+639123456789',
            'email': 'john@example.com'
        }
        
        # Sample investment data
        investment_data = {
            'active_investments': [
                {'name': 'Growth Plan A', 'amount': 5000, 'roi_percentage': 15},
                {'name': 'Premium Plan', 'amount': 10000, 'roi_percentage': 20}
            ],
            'total_invested': 15000,
            'total_earnings': 2250,
            'withdrawable_balance': 1500,
            'non_withdrawable_bonus': 100,
            'roi_percentage': 15,
            'current_investments': [
                {'investment_amount': 5000, 'plan_name': 'Growth Plan A'},
                {'investment_amount': 10000, 'plan_name': 'Premium Plan'}
            ],
            'recent_transactions': [
                {'transaction_type': 'investment', 'amount': 5000, 'created_at': '2025-08-29'},
                {'transaction_type': 'earning', 'amount': 750, 'created_at': '2025-08-29'}
            ]
        }
        
        # Replace Django template variables
        replacements = {
            # User variables
            r'\{\{\s*user\.first_name\|default:"User"\s*\}\}': user_data['first_name'],
            r'\{\{\s*user\.first_name\s*\}\}': user_data['first_name'],
            r'\{\{\s*user\.last_name\s*\}\}': user_data['last_name'],
            r'\{\{\s*user\.phone_number\s*\}\}': user_data['phone_number'],
            r'\{\{\s*user\.email\s*\}\}': user_data['email'],
            
            # Investment variables
            r'\{\{\s*active_investments\|length\s*\}\}': str(len(investment_data['active_investments'])),
            r'\{\{\s*user\.userprofile\.total_invested\|default:"0"\s*\}\}': f"₱{investment_data['total_invested']:,}",
            r'\{\{\s*user\.userprofile\.roi_percentage\|default:"15"\s*\}\}%': f"{investment_data['roi_percentage']}%",
            r'\{\{\s*userprofile\.total_invested\|default:"0"\s*\}\}': f"₱{investment_data['total_invested']:,}",
            r'\{\{\s*userprofile\.roi_percentage\|default:"15"\s*\}\}': str(investment_data['roi_percentage']),
            
            # Remove Django template tags
            r'\{\%\s*extends.*?\%\}': '',
            r'\{\%\s*load.*?\%\}': '',
            r'\{\%\s*block.*?\%\}': '',
            r'\{\%\s*endblock.*?\%\}': '',
            r'\{\%\s*url.*?\%\}': '#',
            r'\{\%\s*static.*?\%\}': '/static/',
            
            # Fix common template patterns
            r'\{\{\s*INVESTMENT_PLAN_NAME\s*\}\}': 'Growth Plan A',
            r'\{\{\s*investment\.amount\|floatformat:2\s*\}\}': '₱5,000.00',
            r'\{\{\s*investment\.plan_name\s*\}\}': 'Growth Plan A',
            r'\{\{\s*investment\.roi_percentage\|default:"0"\s*\}\}': '15',
        }
        
        # Apply replacements
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, str(replacement), content)
        
        # Remove any remaining Django template syntax
        content = re.sub(r'\{\{.*?\}\}', '0', content)
        content = re.sub(r'\{\%.*?\%\}', '', content)
        
        return content

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Starting GrowFi Investment Platform v2.0")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🌐 Port: {port}")
    print(f"⏰ Deploy time: August 29, 2025 - 8:50 PM")
    
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
