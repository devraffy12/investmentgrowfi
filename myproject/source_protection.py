import base64
import gzip
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import re

class SourceProtectionMixin:
    """
    Mixin to protect source code from being easily viewed
    """
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # Obfuscate HTML content
        if hasattr(response, 'content') and response.get('Content-Type', '').startswith('text/html'):
            response.content = self.obfuscate_html(response.content.decode('utf-8')).encode('utf-8')
        
        return response
    
    def obfuscate_html(self, html_content):
        """
        Obfuscate HTML content to make it harder to read
        """
        # Minify HTML - remove unnecessary whitespace and comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Add fake comments and elements to confuse
        obfuscated_comments = [
            '<!-- © 2025 SecureApp - Protected Content -->',
            '<!-- Unauthorized viewing prohibited -->',
            '<!-- Generated content - Do not copy -->',
        ]
        
        # Insert random obfuscated comments
        for comment in obfuscated_comments:
            html_content = html_content.replace('<head>', f'<head>{comment}')
        
        # Add warning message for view source
        warning_script = '''
        <script>
        !function(){
            var _0x=['Unauthorized','Access','Detected','©2025','GrowFi','Protected'];
            console.clear();
            console.log('%c' + _0x[0] + ' ' + _0x[1] + ' ' + _0x[2], 'color:red;font-size:20px;font-weight:bold');
            console.log('%c' + _0x[3] + ' ' + _0x[4] + ' - ' + _0x[5] + ' Content', 'color:red;font-size:14px');
            
            // Monitor for source viewing attempts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && (e.keyCode === 85 || e.keyCode === 83)) {
                    e.preventDefault();
                    alert('Source viewing is not allowed!');
                    return false;
                }
            });
        }();
        </script>
        '''
        
        html_content = html_content.replace('</head>', warning_script + '</head>')
        
        return html_content

def protect_source_view(view_func):
    """
    Decorator to protect views from source code inspection
    """
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if isinstance(response, (HttpResponse, TemplateResponse)):
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Add copyright notice
            response['X-Copyright'] = '© 2025 GrowFi - All Rights Reserved'
            response['X-Protected'] = 'This content is protected by copyright law'
        
        return response
    
    return wrapper
