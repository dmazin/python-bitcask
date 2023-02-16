import http.server
import json
from typing import Dict, Optional, Tuple
import urllib.parse

import constants
import db


class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        """
        Expects a request like `curl http:/?key=foo`
        """
        parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(self.path)
        qs: dict[str, list[str]] = urllib.parse.parse_qs(parsed_url.query)
        key: Optional[str] = qs.get('key', [None])[0]
        if key:
            value: Optional[str] = db.get(key)
            if value:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'value': value}).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

    def do_POST(self) -> None:
        """
        Expects a request like `curl -X POST --json '{"key": "foo", "value": "bar"}' http:/`
        """
        content_length: int = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            return

        post_body_bytes: bytes = self.rfile.read(content_length)
        post_body: Dict = json.loads(post_body_bytes.decode())

        key = post_body.get("key")
        value = post_body.get("value")

        if not key or not value:
            self.send_response(400)
            self.end_headers()
            return

        db.set(key, value)

        self.send_response(201)
        self.end_headers()


if __name__ == "__main__":
    print("debug: server is starting")
    server_address: Tuple[str, int] = (constants.SERVER_ADDRESS, constants.SERVER_PORT)
    httpd = http.server.HTTPServer(server_address, MyHTTPRequestHandler)
    httpd.serve_forever()
