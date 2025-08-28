"""
Security Middleware for GrowFi Platform
© 2025 GrowFi Investment Platform - All Rights Reserved
"""
import logging
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger(__name__)

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


class SessionPersistenceMiddleware:
    """Middleware for PERMANENT session persistence - NO EXPIRATION"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view
        self.process_request(request)
        
        # Get response from view
        response = self.get_response(request)
        
        # Process response after view
        self.process_response(request, response)
        
        return response

    def process_request(self, request):
        """Process request to ensure PERMANENT session persistence"""
        
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return
        
        # Skip for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return
        
        try:
            # ALWAYS renew session to prevent ANY expiration
            # Set to 1 year (practically permanent)
            request.session.set_expiry(365 * 24 * 60 * 60)  # 1 YEAR
            
            # Mark session as modified to ensure it's saved
            request.session.modified = True
            
            # Update session activity tracking
            request.session['last_activity'] = timezone.now().isoformat()
            request.session['activity_count'] = request.session.get('activity_count', 0) + 1
            request.session['never_expire'] = True  # Mark as permanent session
            
            logger.info(f"PERMANENT session renewed for user: {request.user.username}")
            
            # Update Firebase activity (non-blocking)
            try:
                from myproject.views import update_user_in_firebase_realtime_db
                firebase_data = {
                    'last_activity': timezone.now().isoformat(),
                    'is_online': True,
                    'session_active': True,
                    'session_permanent': True,  # Mark as permanent
                    'current_page': request.path,
                    'activity_count': request.session.get('activity_count', 1)
                }
                
                # Non-blocking Firebase update
                update_user_in_firebase_realtime_db(request.user, request.user.username, firebase_data)
                
            except Exception as firebase_error:
                # Don't break the request if Firebase fails
                logger.warning(f"Firebase activity update failed: {firebase_error}")
            
        except Exception as e:
            logger.error(f"PERMANENT session persistence error: {e}")

    def process_response(self, request, response):
        """Process response to finalize PERMANENT session handling"""
        
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return response
        
        try:
            # ALWAYS ensure session is saved for permanent persistence
            if hasattr(request, 'session'):
                # Force session to be saved regardless of modified status
                request.session.save()
                
                # Double-check session expiry is set to 1 year
                if request.session.get_expiry_age() < (364 * 24 * 60 * 60):  # Less than 364 days
                    request.session.set_expiry(365 * 24 * 60 * 60)  # Reset to 1 year
                    request.session.save()
            
        except Exception as e:
            logger.error(f"PERMANENT session save error: {e}")
        
        return response


class AuthenticationRecoveryMiddleware:
    """Middleware to handle authentication recovery in case of issues"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check authentication before processing
        if self.should_check_auth(request):
            self.check_authentication_health(request)
        
        response = self.get_response(request)
        return response

    def should_check_auth(self, request):
        """Determine if authentication should be checked"""
        # Skip for certain paths
        skip_paths = ['/login/', '/register/', '/admin/', '/static/', '/media/']
        
        if any(request.path.startswith(path) for path in skip_paths):
            return False
        
        # Only check for authenticated users
        return request.user.is_authenticated

    def check_authentication_health(self, request):
        """Check and recover authentication if needed"""
        try:
            # Verify user is still active
            if not request.user.is_active:
                logger.warning(f"Inactive user detected: {request.user.username}")
                logout(request)
                return
            
            # Check if profile exists
            from myproject.models import UserProfile
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                # Create missing profile
                profile = UserProfile.objects.create(
                    user=request.user,
                    phone_number=request.user.username
                )
                logger.info(f"Created missing profile for user: {request.user.username}")
            
            # Verify session integrity
            if not request.session.session_key:
                logger.warning(f"Missing session key for user: {request.user.username}")
                # Force session creation
                request.session.create()
                request.session['recovered_session'] = True
                request.session['recovery_time'] = timezone.now().isoformat()
            
        except Exception as e:
            logger.error(f"Authentication health check error: {e}")
