import argparse
import hashlib
import http.server
import socketserver
from threading import Thread
from urllib.parse import ParseResult, parse_qs, urlparse


class ContentHasher:
    def __init__(self, hash_algorithm: str = "sha256", hash_length: int = 5):
        self.hash_map = {}
        self.hash_algorithm = hash_algorithm
        self.hash_length = hash_length

    def hash(self, content: bytes) -> str:
        hash = hashlib.new(self.hash_algorithm)
        hash.update(content)
        return hash.hexdigest()[: self.hash_length]

    def save(self, content: bytes) -> str:
        content_hash = self.hash(content)
        self.hash_map[content_hash] = content
        # TODO - Save the content to a file
        return content_hash


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    hasher: ContentHasher

    def __init__(self, *args, hasher: ContentHasher, **kwargs):
        self.hasher = hasher
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        # Extract the requested URL
        parsed_url: ParseResult = urlparse(self.path)

        content_id = parsed_url.path.split("/")[-1]
        try:
            content = self.hasher.hash_map[content_id]
            self.send_response(302)
            self.send_header("Location", content.decode())
            self.end_headers()
            return
        except KeyError:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        content_length = int(self.headers["Content-Length"])
        content = self.rfile.read(content_length)
        content_hash = self.hasher.save(content)
        print(f"headers: {self.headers}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(f'http://{self.headers["Host"]}/{content_hash}'.encode())


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a simple multithreaded HTTP server."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port number for the server to listen on (default: 8080).",
    )
    parser.add_argument(
        "--hash-algorithm",
        type=str,
        default="sha256",
        help="Hash algorithm to use for content hashing (default: sha256).",
    )
    parser.add_argument(
        "--hash-length",
        type=int,
        default=5,
        help="Length of the hash to generate (default: 5).",
    )
    return parser.parse_args()


def run_server(
    port: int = 8080, hash_algorithm: str = "sha256", hash_length: int = 5
) -> None:
    """Run the multithreaded HTTP server on the specified port."""
    server_address: tuple[str, int] = ("", port)

    hasher = ContentHasher(hash_algorithm=hash_algorithm, hash_length=hash_length)

    # Create the server with the custom handler
    def handler(*args, **kwargs):
        return CustomHTTPRequestHandler(*args, hasher=hasher, **kwargs)

    httpd: ThreadedHTTPServer = ThreadedHTTPServer(server_address, handler)

    print(f"Serving on port {server_address[1]}")

    # Start the server in a separate thread
    server_thread: Thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = (
        True  # Allows the program to exit if the main thread terminates
    )
    server_thread.start()
    print("Server running in a separate thread.")
    server_thread.join()
    httpd.shutdown()


def main() -> None:
    args = parse_arguments()
    run_server(
        port=args.port, hash_algorithm=args.hash_algorithm, hash_length=args.hash_length
    )


if __name__ == "__main__":
    main()
