"""
Security Middleware for GrowFi Platform
© 2025 GrowFi Investment Platform - All Rights Reserved
"""

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
        
        # Disable caching for sensitive pages
        if 'dashboard' in request.path or 'profile' in request.path:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Content protection headers
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        
        return response


class AntiSourceViewMiddleware:
    """Middleware to detect and prevent source code viewing attempts"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for suspicious user agents or patterns
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Block known source viewing tools
        blocked_agents = [
            'wget', 'curl', 'scrapy', 'spider', 'crawler', 
            'bot', 'scraper', 'httpie', 'python-requests'
        ]
        
        if any(agent in user_agent for agent in blocked_agents):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access Denied - Automated Access Not Allowed")
        
        response = self.get_response(request)
        
        # Add copyright notice in response headers
        response['X-Copyright'] = '© 2025 GrowFi Investment Platform - All Rights Reserved'
        response['X-Legal-Notice'] = 'Unauthorized reproduction is prohibited'
        
        return response
