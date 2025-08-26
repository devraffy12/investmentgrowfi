// Enhanced Source Code Protection System v2.0
(function() {
    'use strict';
    
    // Obfuscated protection functions
    const _0x4a5f = ['keydown', 'contextmenu', 'selectstart', 'dragstart', 'copy', 'cut'];
    const _0x2b8c = ['F12', 'DevTools', 'Inspector', 'Console', 'Sources', 'Network'];
    const _0x7d9e = ['Ctrl+U', 'Ctrl+S', 'Ctrl+Shift+I', 'Ctrl+Shift+J', 'Ctrl+Shift+C'];
    
    // Clear console and add warnings
    if (window.console) {
        console.clear();
        console.log('%c🚫 STOP!', 'color: #ff0000; font-size: 50px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);');
        console.log('%c⚠️  UNAUTHORIZED ACCESS DETECTED', 'color: #ff6600; font-size: 24px; font-weight: bold;');
        console.log('%c📜 This is a browser feature intended for developers only.', 'color: #0066cc; font-size: 16px;');
        console.log('%c🔒 Viewing, copying, or distributing this code is strictly prohibited.', 'color: #cc0000; font-size: 16px;');
        console.log('%c© 2025 GrowFi - All Rights Reserved', 'color: #666666; font-size: 14px; font-style: italic;');
        console.log('%c🛡️  This content is protected by copyright law and security measures.', 'color: #009900; font-size: 14px;');
        
        // Override console methods
        const originalConsole = window.console;
        window.console = new Proxy(originalConsole, {
            get(target, prop) {
                if (typeof target[prop] === 'function') {
                    return function(...args) {
                        if (prop === 'clear') {
                            setTimeout(() => {
                                originalConsole.log('%c🚫 Console Access Blocked', 'color: red; font-size: 20px;');
                            }, 100);
                        }
                        return target[prop].apply(target, args);
                    };
                }
                return target[prop];
            }
        });
    }
    
    // Advanced DevTools detection
    let devtools = {
        open: false,
        orientation: null
    };
    
    // Multiple detection methods
    const checkDevTools = () => {
        const widthThreshold = window.outerWidth - window.innerWidth > 160;
        const heightThreshold = window.outerHeight - window.innerHeight > 160;
        
        if (widthThreshold || heightThreshold) {
            if (!devtools.open) {
                devtools.open = true;
                handleDevToolsOpen();
            }
        } else {
            devtools.open = false;
        }
    };
    
    // Handle DevTools detection
    const handleDevToolsOpen = () => {
        document.body.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: #ffffff;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-family: 'Arial', sans-serif;
                z-index: 999999;
                text-align: center;
                padding: 20px;
                box-sizing: border-box;
            ">
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 15px;
                    padding: 40px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                ">
                    <h1 style="
                        font-size: 48px;
                        margin: 0 0 20px 0;
                        color: #ff4444;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                    ">🚫 ACCESS DENIED</h1>
                    <p style="
                        font-size: 24px;
                        margin: 0 0 15px 0;
                        color: #ffaa00;
                    ">⚠️ Unauthorized Developer Tools Access Detected</p>
                    <p style="
                        font-size: 18px;
                        margin: 0 0 15px 0;
                        color: #ffffff;
                        opacity: 0.9;
                    ">🔒 This application is protected by copyright law.</p>
                    <p style="
                        font-size: 16px;
                        margin: 0 0 30px 0;
                        color: #cccccc;
                    ">Viewing, copying, or reverse engineering is strictly prohibited.</p>
                    <div style="
                        font-size: 14px;
                        color: #888888;
                        border-top: 1px solid rgba(255, 255, 255, 0.2);
                        padding-top: 20px;
                        margin-top: 20px;
                    ">
                        © 2025 GrowFi Investment Platform<br>
                        All Rights Reserved | Protected Content
                    </div>
                </div>
            </div>
        `;
        
        // Clear page after showing warning
        setTimeout(() => {
            window.location.href = 'about:blank';
        }, 3000);
    };
    
    // Enhanced keyboard event blocking
    document.addEventListener('keydown', function(e) {
        // Block F12, F7, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U, Ctrl+S
        const blockedKeys = [
            e.keyCode === 123, // F12
            e.keyCode === 118, // F7
            (e.ctrlKey && e.shiftKey && e.keyCode === 73), // Ctrl+Shift+I
            (e.ctrlKey && e.shiftKey && e.keyCode === 74), // Ctrl+Shift+J
            (e.ctrlKey && e.shiftKey && e.keyCode === 67), // Ctrl+Shift+C
            (e.ctrlKey && e.keyCode === 85), // Ctrl+U
            (e.ctrlKey && e.keyCode === 83), // Ctrl+S
            (e.metaKey && e.altKey && e.keyCode === 73), // Cmd+Option+I (Mac)
            (e.metaKey && e.altKey && e.keyCode === 67), // Cmd+Option+C (Mac)
        ];
        
        if (blockedKeys.some(blocked => blocked)) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Show warning
            if (!document.getElementById('warning-toast')) {
                showWarningToast();
            }
            
            return false;
        }
    }, true);
    
    // Show warning toast
    const showWarningToast = () => {
        const toast = document.createElement('div');
        toast.id = 'warning-toast';
        toast.innerHTML = '🚫 Developer tools access is restricted!';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            font-size: 16px;
            font-weight: bold;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(255, 68, 68, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.2);
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    };
    
    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Disable right-click context menu
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        e.stopPropagation();
        showWarningToast();
        return false;
    }, true);
    
    // Disable text selection
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    }, true);
    
    // Disable drag and drop
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    }, true);
    
    // Disable copy/cut operations
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        e.clipboardData.setData('text/plain', '© 2025 GrowFi - Content Protected');
        showWarningToast();
        return false;
    }, true);
    
    document.addEventListener('cut', function(e) {
        e.preventDefault();
        return false;
    }, true);
    
    // Monitor window size changes for DevTools detection
    setInterval(checkDevTools, 200);
    
    // Disable printing
    window.addEventListener('beforeprint', function(e) {
        e.preventDefault();
        showWarningToast();
        return false;
    });
    
    // Disable Ctrl+P
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 80) {
            e.preventDefault();
            showWarningToast();
            return false;
        }
    });
    
    // Performance-based debugger detection
    setInterval(function() {
        const start = performance.now();
        debugger;
        const duration = performance.now() - start;
        
        if (duration > 100) {
            handleDevToolsOpen();
        }
    }, 2000);
    
    // Disable source viewing through other methods
    Object.defineProperty(document, 'hidden', {
        get: function() {
            handleDevToolsOpen();
            return true;
        }
    });
    
    // Override toString methods
    Function.prototype.toString = function() {
        return 'function() { [Protected Code] }';
    };
    
    // Monitor for iframe injection attempts
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.tagName === 'IFRAME' && !node.src.includes(window.location.origin)) {
                    node.remove();
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Final message
    console.log('%c🛡️ Source Protection System Active', 'color: #00aa00; font-size: 16px; font-weight: bold;');
    
})();
