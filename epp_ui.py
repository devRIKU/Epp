"""
E++ UI Runtime Module
Provides webview windows, HTML rendering, and web page fetching for the E++ language.
"""

import webview
import threading
import time
import os
import json
import urllib.request
import urllib.error
from html.parser import HTMLParser


# ─── HTML Text Extractor ─────────────────────────────────────────────────────

class _HTMLTextExtractor(HTMLParser):
    """Strips tags and extracts plain readable text from HTML."""
    def __init__(self):
        super().__init__()
        self._result = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head'):
            self._skip = False
        if tag in ('p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'):
            self._result.append('\n')

    def handle_data(self, data):
        if not self._skip:
            self._result.append(data.strip())

    def get_text(self):
        return ' '.join(filter(None, self._result))


# ─── Browser Shell HTML (navigation bar + content iframe) ────────────────────

BROWSER_SHELL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { height: 100%; overflow: hidden; }
    body {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        background: #0f0c29;
        display: flex;
        flex-direction: column;
    }
    .nav-bar {
        display: flex;
        align-items: center;
        padding: 7px 10px;
        background: linear-gradient(180deg, #1e1e3a, #16213e);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        gap: 6px;
        flex-shrink: 0;
        user-select: none;
        -webkit-user-select: none;
    }
    .nav-btn {
        width: 30px; height: 30px;
        border: none;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.06);
        color: #8888aa;
        font-size: 15px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }
    .nav-btn:hover {
        background: rgba(233, 69, 96, 0.25);
        color: #e0e0ff;
    }
    .nav-btn:active { transform: scale(0.9); }
    .url-bar {
        flex: 1;
        height: 30px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 0 14px;
        background: rgba(0, 0, 0, 0.35);
        color: #c8c8e0;
        font-size: 13px;
        outline: none;
        transition: all 0.25s ease;
        min-width: 0;
    }
    .url-bar:focus {
        border-color: rgba(233, 69, 96, 0.5);
        box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.12);
        background: rgba(0, 0, 0, 0.5);
    }
    .url-bar::placeholder { color: rgba(136, 136, 170, 0.5); }
    .url-bar::selection { background: rgba(233, 69, 96, 0.35); }
    .go-btn {
        height: 30px;
        padding: 0 14px;
        border: none;
        border-radius: 8px;
        background: linear-gradient(135deg, #e94560, #7b2ff7);
        color: #fff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        cursor: pointer;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }
    .go-btn:hover {
        box-shadow: 0 2px 12px rgba(233, 69, 96, 0.35);
        transform: translateY(-1px);
    }
    .go-btn:active { transform: scale(0.95); }
    #contentFrame {
        flex: 1;
        border: none;
        width: 100%;
        background: #fff;
    }
    /* Loading spinner shown briefly while content loads */
    .loading-overlay {
        position: absolute;
        top: 44px; left: 0; right: 0; bottom: 0;
        display: none;
        align-items: center;
        justify-content: center;
        background: rgba(15, 12, 41, 0.85);
        z-index: 10;
    }
    .loading-overlay.active { display: flex; }
    .spinner {
        width: 36px; height: 36px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: #e94560;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div class="nav-bar">
    <button class="nav-btn" onclick="goBack()" title="Back">&#8592;</button>
    <button class="nav-btn" onclick="goForward()" title="Forward">&#8594;</button>
    <button class="nav-btn" onclick="doRefresh()" title="Refresh">&#8635;</button>
    <input class="url-bar" id="urlInput" type="text"
           placeholder="Enter a URL..."
           onkeydown="if(event.key==='Enter')navigate()"
           spellcheck="false" autocomplete="off">
    <button class="go-btn" onclick="navigate()">GO</button>
</div>
<div class="loading-overlay" id="loadingOverlay"><div class="spinner"></div></div>
<iframe id="contentFrame" src="about:blank"></iframe>
<script>
    var currentUrl = '';
    var loadingTimer = null;

    function showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
        // Auto-hide after 4 seconds max
        clearTimeout(loadingTimer);
        loadingTimer = setTimeout(hideLoading, 4000);
    }
    function hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
        clearTimeout(loadingTimer);
    }

    function navigate() {
        var url = document.getElementById('urlInput').value.trim();
        if (!url) return;
        if (!/^(https?:|file:|about:|data:)/.test(url)) {
            url = 'https://' + url;
        }
        loadUrl(url);
    }

    function goBack() {
        try { document.getElementById('contentFrame').contentWindow.history.back(); }
        catch(e) {}
    }
    function goForward() {
        try { document.getElementById('contentFrame').contentWindow.history.forward(); }
        catch(e) {}
    }
    function doRefresh() {
        try {
            document.getElementById('contentFrame').contentWindow.location.reload();
        } catch(e) {
            if (currentUrl) {
                document.getElementById('contentFrame').src = currentUrl;
            }
        }
    }

    function loadUrl(url) {
        showLoading();
        document.getElementById('urlInput').value = url;
        document.getElementById('contentFrame').src = url;
        currentUrl = url;
    }

    function loadSrcdoc(html) {
        document.getElementById('contentFrame').srcdoc = html;
        document.getElementById('urlInput').value = 'inline content';
        currentUrl = 'about:srcdoc';
    }

    // Hide loading spinner when iframe finishes loading
    document.getElementById('contentFrame').addEventListener('load', hideLoading);

    // Periodically try to sync the URL bar with iframe's current location
    setInterval(function() {
        try {
            var loc = document.getElementById('contentFrame').contentWindow.location.href;
            if (loc && loc !== 'about:blank' && loc !== 'about:srcdoc') {
                document.getElementById('urlInput').value = loc;
                currentUrl = loc;
            }
        } catch(e) {
            // Cross-origin: can't read URL – keep showing the last known URL
        }
    }, 500);
</script>
</body>
</html>"""


# ─── Window Manager (Singleton) ──────────────────────────────────────────────

class EppWindowManager:
    """Manages all E++ webview windows."""

    def __init__(self):
        self._windows = {}          # title -> webview.Window
        self._pending_actions = []  # actions to run after event loop starts
        self._started = False

    def create_window(self, title, width=800, height=600):
        """Create a new named webview window with a built-in URL/navigation bar."""
        win = webview.create_window(
            title,
            html=BROWSER_SHELL_HTML,
            width=width,
            height=height,
        )
        self._windows[title] = win
        return win

    def set_html(self, title, html_content):
        """Set the HTML content of a named window (queued until event loop)."""
        self._pending_actions.append(('set_html', title, html_content))

    def load_file(self, title, filepath):
        """Load an HTML file into a named window (queued until event loop)."""
        abs_path = os.path.abspath(filepath)
        self._pending_actions.append(('load_file', title, abs_path))

    def load_url(self, title, url):
        """Navigate a named window to a URL (queued until event loop)."""
        self._pending_actions.append(('load_url', title, url))

    def _run_pending(self):
        """Execute all queued actions once the event loop is running."""
        # Give the browser shell a moment to fully render
        time.sleep(0.8)
        for action in self._pending_actions:
            kind = action[0]
            title = action[1]
            win = self._windows.get(title)
            if not win:
                continue
            try:
                if kind == 'set_html':
                    # Inject HTML into the iframe via the srcdoc approach
                    html_json = json.dumps(action[2])
                    win.evaluate_js(f"loadSrcdoc({html_json})")
                elif kind == 'load_file':
                    file_url = 'file:///' + action[2].replace('\\', '/')
                    url_json = json.dumps(file_url)
                    win.evaluate_js(f"loadUrl({url_json})")
                elif kind == 'load_url':
                    url_json = json.dumps(action[2])
                    win.evaluate_js(f"loadUrl({url_json})")
            except Exception as e:
                print(f"E++ UI Warning: could not perform {kind} on '{title}': {e}")
        self._pending_actions.clear()

    def start(self):
        """Start the webview event loop (must be called from the main thread)."""
        if not self._started and self._windows:
            self._started = True
            # Pass _run_pending as the startup callback so queued
            # actions execute once the event loop is alive.
            webview.start(func=self._run_pending)


# Global singleton
_manager = EppWindowManager()


# ─── Public API (called from transpiled E++ code) ────────────────────────────

def epp_create_window(title, width=800, height=600):
    """E++: create window titled 'X'."""
    _manager.create_window(title, width, height)


def epp_set_window_html(title, html_content):
    """E++: set window content of 'X' to '...'."""
    _manager.set_html(title, html_content)


def epp_load_file_in_window(title, filepath):
    """E++: load file 'Y' into window 'X'."""
    _manager.load_file(title, filepath)


def epp_load_url_in_window(title, url):
    """E++: open url 'U' in window 'X'."""
    _manager.load_url(title, url)


def epp_show_windows():
    """E++: show windows."""
    _manager.start()


def epp_fetch_page(url):
    """E++: fetch page 'url'. Returns the raw HTML string."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'E++ Language/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"Error fetching page: {e}"


def epp_read_html_text(html_string):
    """E++: read text from html. Strips tags and returns plain text."""
    extractor = _HTMLTextExtractor()
    extractor.feed(html_string)
    return extractor.get_text()


def epp_read_html_file(filepath):
    """E++: read html file 'X'. Returns raw HTML content from disk."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
