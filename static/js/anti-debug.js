// Advanced anti-debugging and source protection
(function() {
    'use strict';

    // Obfuscated variable names
    let a = 0, b = 0, c = 0;
    
    // Console protection
    const originalConsole = window.console;
    window.console = {
        log: function() { return false; },
        warn: function() { return false; },
        error: function() { return false; },
        info: function() { return false; },
        debug: function() { return false; },
        trace: function() { return false; },
        dir: function() { return false; },
        dirxml: function() { return false; },
        table: function() { return false; },
        clear: function() { return false; }
    };

    // DevTools detection using timing
    let devtools = {
        open: false,
        orientation: null
    };

    setInterval(function() {
        if (window.outerHeight - window.innerHeight > 200 || 
            window.outerWidth - window.innerWidth > 200) {
            if (!devtools.open) {
                devtools.open = true;
                window.location.href = 'about:blank';
            }
        } else {
            devtools.open = false;
        }
    }, 500);

    // Advanced keyboard blocking
    document.addEventListener('keydown', function(e) {
        // Block F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U, Ctrl+S, F7
        if (e.keyCode === 123 || 
            (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74)) ||
            (e.ctrlKey && e.keyCode === 85) ||
            (e.ctrlKey && e.keyCode === 83) ||
            e.keyCode === 118) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });

    // Block text selection and drag
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    });

    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    });

    // Advanced right-click protection
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
    });

    // Disable printing
    window.addEventListener('beforeprint', function(e) {
        e.preventDefault();
        return false;
    });

    // Mouse event protection
    document.addEventListener('mousedown', function(e) {
        if (e.button === 2) { // Right click
            e.preventDefault();
            return false;
        }
    });

    // Block common debug attempts
    Object.defineProperty(window, 'console', {
        get: function() {
            return originalConsole;
        },
        set: function(val) {
            // Ignore attempts to modify console
        }
    });

    // Detect debug tools
    let element = new Image();
    Object.defineProperty(element, 'id', {
        get: function() {
            window.location.href = 'about:blank';
        }
    });

    // Performance monitoring for debugging detection
    let start = performance.now();
    debugger;
    let duration = performance.now() - start;
    if (duration > 100) {
        window.location.href = 'about:blank';
    }

    // Clear all intervals and timeouts that might be used for debugging
    setInterval(function() {
        a++; b++; c++;
        if (a > 1000000) a = 0;
        if (b > 1000000) b = 0;
        if (c > 1000000) c = 0;
    }, 1000);

})();

// Additional protection layer
!function() {
    function detectDevTools() {
        if (window.devtools.open) {
            document.body.innerHTML = '';
            window.location.href = 'data:text/html,<h1>Access Denied</h1>';
        }
    }

    // Check every second
    setInterval(detectDevTools, 1000);

    // Prevent source viewing shortcuts
    window.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode === 67) { // Ctrl+Shift+C
            e.preventDefault();
            return false;
        }
        if (e.keyCode === 116) { // F5 refresh
            if (e.ctrlKey) { // Ctrl+F5 hard refresh
                e.preventDefault();
                return false;
            }
        }
    });
}();
