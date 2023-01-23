import http.server
import json
from typing import Optional, Tuple
import urllib.parse

import constants
import db


class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
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
        pass


if __name__ == "__main__":
    server_address: Tuple[str, int] = (constants.SERVER_ADDRESS, constants.SERVER_PORT)
    httpd = http.server.HTTPServer(server_address, MyHTTPRequestHandler)
    httpd.serve_forever()
