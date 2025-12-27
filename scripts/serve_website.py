#!/usr/bin/env python3
"""Simple HTTP server to test the static website locally."""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
PROJECT_ROOT = Path(__file__).parent.parent
WEBSITE_DIR = PROJECT_ROOT / "website"
DATA_DIR = PROJECT_ROOT / "data"


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler to serve from website directory and data directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def translate_path(self, path):
        """Translate URL path to local file path.

        Serves website files from website/ and data files from data/
        """
        # Get the original translated path
        path = super().translate_path(path)

        # If requesting root, serve from website/index.html
        if path.endswith(str(PROJECT_ROOT)):
            return str(WEBSITE_DIR / "index.html")

        # Convert to Path for easier manipulation
        path_obj = Path(path)

        # If path is under PROJECT_ROOT/data, serve it as-is
        if str(DATA_DIR) in str(path_obj):
            return path

        # Otherwise, assume it's a website file
        relative_to_root = path_obj.relative_to(PROJECT_ROOT)
        website_path = WEBSITE_DIR / relative_to_root

        if website_path.exists():
            return str(website_path)

        # Fall back to original path
        return path


def main():
    """Start the local web server."""
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"🌐 Server started at {url}")
        print(f"📁 Serving website from: {WEBSITE_DIR}")
        print(f"📁 Serving data from: {DATA_DIR}")
        print(f"Press Ctrl+C to stop the server")

        # Try to open browser automatically
        try:
            webbrowser.open(url)
            print(f"✓ Opened {url} in your browser")
        except Exception:
            print(f"Please open {url} in your browser manually")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")


if __name__ == "__main__":
    main()
