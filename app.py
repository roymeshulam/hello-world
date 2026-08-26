#!/usr/bin/env python3
"""Minimal Hello World HTTP application for hello-world.roymeshulam.com."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PAGE = b"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>Hello World</title></head><body><h1>Hello World</h1></body></html>"


class HelloWorldHandler(BaseHTTPRequestHandler):
    """Return a minimal page with a single Hello World heading."""

    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path not in ("/", "/healthz"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(PAGE)

    def do_HEAD(self) -> None:
        self.do_GET()

    def log_message(self, format: str, *args: object) -> None:
        # Requests are visible in the systemd journal without duplicate logs.
        print("%s - %s" % (self.address_string(), format % args), flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8001), HelloWorldHandler)
    print("Serving Hello World on http://127.0.0.1:8001", flush=True)
    server.serve_forever()
