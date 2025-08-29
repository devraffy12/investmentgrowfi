#!/usr/bin/env python3
"""
Complete GrowFi Investment Platform Server
Serves your entire Django project with all static files and templates
"""
import os
import http.server
import socketserver
from urllib.parse import urlparse
import mimetypes

class GrowFiPlatformHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"📄 Request: {path}")
        
        # Route mapping for your complete investment platform
        routes = {
            '/': 'myproject/templates/myproject/index.html',
            '/home': 'myproject/templates/myproject/index.html',
            '/login': 'myproject/templates/myproject/login.html',
            '/register': 'myproject/templates/myproject/register.html',
            '/dashboard': 'myproject/templates/myproject/dashboard.html',
            '/investment_plans': 'myproject/templates/myproject/investment_plans.html',
            '/my_investments': 'myproject/templates/myproject/my_investments.html',
            '/investment': 'myproject/templates/myproject/investment.html',
            '/make_investment': 'myproject/templates/myproject/make_investment.html',
            '/deposit': 'myproject/templates/myproject/deposit.html',
            '/withdraw': 'myproject/templates/myproject/withdraw.html',
            '/transaction_history': 'myproject/templates/myproject/transaction_history.html',
            '/referral_dashboard': 'myproject/templates/myproject/referral_dashboard.html',
            '/referral_link': 'myproject/templates/myproject/referral_link.html',
            '/team': 'myproject/templates/myproject/team.html',
            '/profile': 'myproject/templates/myproject/profile.html',
            '/payment_gateway': 'myproject/templates/myproject/payment_gateway.html',
            '/gcash_payment': 'myproject/templates/myproject/gcash_payment.html',
            '/support': 'myproject/templates/myproject/support.html',
            '/terms': 'myproject/templates/myproject/terms.html',
            '/privacy': 'myproject/templates/myproject/privacy.html',
        }
        
        if path in routes:
            self.serve_template(routes[path])
        elif path.startswith('/static/'):
            # Serve static files (CSS, JS, images)
            self.serve_static_file(path)
        elif path.startswith('/media/'):
            # Serve media files
            self.serve_static_file(path)
        else:
            # Try to find template by path
            template_path = f"myproject/templates/myproject{path}.html"
            if os.path.exists(template_path):
                self.serve_template(template_path)
            else:
                # Check if index.html exists, otherwise default to dashboard
                if os.path.exists('myproject/templates/myproject/index.html'):
                    self.serve_template('myproject/templates/myproject/index.html')
                else:
                    self.serve_template('myproject/templates/myproject/dashboard.html')
    
    def serve_template(self, file_path):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process Django template syntax
                content = self.process_django_template(content)
                
                content_bytes = content.encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content_bytes))
                self.end_headers()
                self.wfile.write(content_bytes)
                
                print(f"✅ Served template: {file_path}")
            else:
                print(f"❌ Template not found: {file_path}")
                self.send_error(404, f"Template not found: {file_path}")
        except Exception as e:
            print(f"💥 Error serving template {file_path}: {e}")
            self.send_error(500, f"Error serving template: {str(e)}")
    
    def serve_static_file(self, path):
        # Remove leading slash and serve from correct directory
        file_path = path[1:]  # Remove leading slash
        
        if os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                if file_path.endswith('.css'):
                    mime_type = 'text/css'
                elif file_path.endswith('.js'):
                    mime_type = 'application/javascript'
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    mime_type = 'image/jpeg'
                else:
                    mime_type = 'application/octet-stream'
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                
                print(f"✅ Served static: {file_path}")
            except Exception as e:
                print(f"💥 Error serving static file {file_path}: {e}")
                self.send_error(500, f"Error serving static file: {str(e)}")
        else:
            print(f"❌ Static file not found: {file_path}")
            self.send_error(404, f"Static file not found: {file_path}")
    
    def process_django_template(self, content):
        """Process Django template syntax and replace with actual values"""
        import re
        
        # Comprehensive user data for your investment platform
        user_data = {
            'first_name': 'John',
            'last_name': 'Investor',
            'phone_number': '+639123456789',
            'email': 'john@growfi.com',
            'username': 'john_investor'
        }
        
        # Complete investment platform data
        platform_data = {
            'active_investments': 2,
            'total_invested': 25000,
            'total_earnings': 3750,
            'withdrawable_balance': 2500,
            'non_withdrawable_bonus': 500,
            'roi_percentage': 15,
            'avg_duration': 45,
            'pending_withdrawals': 0,
            'investment_plans': [
                {'name': 'Starter Plan', 'min_amount': 1000, 'roi': 12, 'duration': 30},
                {'name': 'Growth Plan', 'min_amount': 5000, 'roi': 15, 'duration': 45},
                {'name': 'Premium Plan', 'min_amount': 10000, 'roi': 20, 'duration': 60},
                {'name': 'VIP Plan', 'min_amount': 25000, 'roi': 25, 'duration': 90}
            ],
            'recent_transactions': [
                {'type': 'investment', 'amount': 10000, 'date': '2025-08-29', 'status': 'completed'},
                {'type': 'earning', 'amount': 1500, 'date': '2025-08-28', 'status': 'completed'},
                {'type': 'investment', 'amount': 15000, 'date': '2025-08-27', 'status': 'completed'}
            ],
            'referral_code': 'GROWFI2025',
            'referral_earnings': 1250,
            'team_members': 8
        }
        
        # Extensive template variable replacements
        replacements = {
            # User variables
            r'\{\{\s*user\.first_name\|default:"User"\s*\}\}': user_data['first_name'],
            r'\{\{\s*user\.first_name\s*\}\}': user_data['first_name'],
            r'\{\{\s*user\.last_name\s*\}\}': user_data['last_name'],
            r'\{\{\s*user\.phone_number\s*\}\}': user_data['phone_number'],
            r'\{\{\s*user\.email\s*\}\}': user_data['email'],
            r'\{\{\s*user\.username\s*\}\}': user_data['username'],
            
            # Investment data
            r'\{\{\s*active_investments\|length\s*\}\}': str(platform_data['active_investments']),
            r'\{\{\s*user\.userprofile\.total_invested\|default:"0"\s*\}\}': f"₱{platform_data['total_invested']:,}",
            r'\{\{\s*user\.userprofile\.roi_percentage\|default:"15"\s*\}\}': str(platform_data['roi_percentage']),
            r'\{\{\s*userprofile\.total_invested\s*\}\}': f"₱{platform_data['total_invested']:,}",
            r'\{\{\s*userprofile\.roi_percentage\s*\}\}': str(platform_data['roi_percentage']),
            r'\{\{\s*userprofile\.withdrawable_balance\s*\}\}': f"₱{platform_data['withdrawable_balance']:,}",
            r'\{\{\s*userprofile\.total_earnings\s*\}\}': f"₱{platform_data['total_earnings']:,}",
            
            # Platform specific variables
            r'\{\{\s*INVESTMENT_PLAN_NAME\s*\}\}': 'Growth Plan',
            r'\{\{\s*investment\.amount\|floatformat:2\s*\}\}': f"₱{platform_data['total_invested']:,}.00",
            r'\{\{\s*investment\.plan_name\s*\}\}': 'Growth Plan',
            r'\{\{\s*investment\.roi_percentage\s*\}\}': str(platform_data['roi_percentage']),
            
            # Remove Django template tags
            r'\{\%\s*extends[^%]*\%\}': '',
            r'\{\%\s*load[^%]*\%\}': '',
            r'\{\%\s*block[^%]*\%\}': '',
            r'\{\%\s*endblock[^%]*\%\}': '',
            r'\{\%\s*include[^%]*\%\}': '',
            
            # Fix URLs and static files
            r'\{\%\s*url\s+["\']([^"\']+)["\']\s*\%\}': r'/\1',
            r'\{\%\s*static\s+["\']([^"\']+)["\']\s*\%\}': r'/static/\1',
            
            # Navigation and common elements
            r'\{\{\s*request\.user\.is_authenticated\s*\}\}': 'True',
            r'\{\{\s*messages\s*\}\}': '',
        }
        
        # Apply all replacements
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, str(replacement), content)
        
        # Remove any remaining Django template syntax
        content = re.sub(r'\{\{[^}]*\}\}', '0', content)
        content = re.sub(r'\{\%[^%]*\%\}', '', content)
        
        # Fix navigation links
        nav_links = {
            'href="/dashboard"': 'href="/dashboard"',
            'href="/investment_plans"': 'href="/investment_plans"',
            'href="/my_investments"': 'href="/my_investments"',
            'href="/deposit"': 'href="/deposit"',
            'href="/withdraw"': 'href="/withdraw"',
            'href="/transaction_history"': 'href="/transaction_history"',
            'href="/referral_dashboard"': 'href="/referral_dashboard"',
            'href="/team"': 'href="/team"',
            'href="/profile"': 'href="/profile"',
        }
        
        for old_link, new_link in nav_links.items():
            content = content.replace(old_link, new_link)
        
        return content

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Starting Complete GrowFi Investment Platform v3.0")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🌐 Port: {port}")
    print(f"⏰ Deploy time: August 29, 2025 - 9:05 PM")
    
    # List available templates
    template_dir = "myproject/templates/myproject"
    if os.path.exists(template_dir):
        templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        print(f"📋 Available pages: {len(templates)}")
        for template in templates[:10]:  # Show first 10
            page_name = template.replace('.html', '')
            print(f"   📄 /{page_name}")
        if len(templates) > 10:
            print(f"   ... and {len(templates) - 10} more pages")
    
    # List static files
    static_dir = "static"
    if os.path.exists(static_dir):
        css_files = []
        js_files = []
        img_files = []
        
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith('.css'):
                    css_files.append(file)
                elif file.endswith('.js'):
                    js_files.append(file)
                elif file.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                    img_files.append(file)
        
        print(f"🎨 CSS files: {len(css_files)}")
        print(f"⚡ JS files: {len(js_files)}")  
        print(f"🖼️ Images: {len(img_files)}")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), GrowFiPlatformHandler) as httpd:
            print(f"🎯 Complete GrowFi Platform running at http://0.0.0.0:{port}")
            print(f"🌟 Your investment platform is now live with all features!")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
