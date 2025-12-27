#!/usr/bin/env python3
"""Simple HTTP server to test the static website locally."""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
WEBSITE_DIR = Path(__file__).parent.parent / "website"


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler to serve from website directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBSITE_DIR), **kwargs)


def main():
    """Start the local web server."""
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"🌐 Server started at {url}")
        print(f"📁 Serving files from: {WEBSITE_DIR}")
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
