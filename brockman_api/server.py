import argparse
import http.server
import json
import random
import socket
import socketserver
import string
from threading import Thread


def send_irc_message(channel: str, message: str) -> None:
    # generate a random alphanumeric nick
    nick = "api_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("brockman.news", 6667))
    conn.send(f"NICK {nick}\n".encode())
    conn.send(f"USER {nick} 0 * :{nick}\n".encode())
    conn.send(b"JOIN #all\n")
    conn.send(f"PRIVMSG {channel} :{message}\n".encode())
    conn.close()


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    irc_server: str
    control_channel: str

    def __init__(self, *args, irc_server: str, control_channel: str, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        #
        # example body: { "feed": "https://www.example.com/rss", nick: "example" }
        #
        content_length = int(self.headers["Content-Length"])
        content = self.rfile.read(content_length)
        body = json.loads(content)
        send_irc_message(
            channel="#all", message=f"brockman: add {body['nick']} {body['feed']}"
        )
        self.send_response(200)
        self.end_headers()


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
        "--irc-server",
        type=int,
        default="brockman.news",
        help="hostname of the IRC server",
    )
    parser.add_argument(
        "--control-channel",
        type=str,
        default="#all",
        help="chanel to send control messages to",
    )
    return parser.parse_args()


def run_server(
    port: int = 8080,
    irc_server: str = "brockman.news",
    control_channel: str = "#all",
) -> None:
    """Run the multithreaded HTTP server on the specified port."""
    server_address: tuple[str, int] = ("", port)

    # Create the server with the custom handler
    def handler(*args, **kwargs):
        return CustomHTTPRequestHandler(
            *args,
            irc_server=irc_server,
            control_channel=control_channel,
            **kwargs,
        )

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
        port=args.port,
    )


if __name__ == "__main__":
    main()
