import argparse
import http.server
import json
import logging
import random
import socket
import socketserver
import string
from threading import Thread

log = logging.getLogger("brockman_api.server")


def send_irc_message(server: str, channel: str, message: str) -> None:
    # generate a random alphanumeric nick
    nick = "api_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    addrinfo = socket.getaddrinfo(server, 6667, socket.AF_UNSPEC, socket.SOCK_STREAM)
    conn = None
    for res in addrinfo:
        af, socktype, proto, canonname, sa = res
        try:
            conn = socket.socket(af, socktype, proto)
            conn.connect(sa)
            break
        except OSError:
            if conn:
                conn.close()
    if conn is None:
        raise OSError("Could not open socket")
    conn.settimeout(1.0)
    log.info("connected to server")
    msg = f"USER {nick} 0 * :{nick}\nNICK {nick}\nJOIN #all\n"
    log.info(f"sending {msg}")
    conn.send(msg.encode())
    data = None
    buffer = b""  # A bytes object to store received data
    while True:
        try:
            data = conn.recv(1024)  # Adjust buffer size as needed
            if data:  # If no data is received, the connection is likely closed
                buffer += data
        except TimeoutError:
            break
    log.info(buffer.decode())
    msg = f"PRIVMSG {channel} :{message}\n"
    log.info(f"sending {msg}")
    conn.send(msg.encode())
    log.info(conn.recv(2048).decode())
    log.info("closing connection")
    conn.close()


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    irc_server: str
    control_channel: str

    def __init__(self, *args, irc_server: str, control_channel: str, **kwargs):
        self.irc_server = irc_server
        self.control_channel = control_channel
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
        log.info(
            f"sending message to follow {body['feed']} to {self.irc_server} {self.control_channel}"
        )
        send_irc_message(
            server=self.irc_server,
            channel=self.control_channel,
            message=f"brockman: add {body['nick']} {body['feed']}",
        )
        log.info("message sent")
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
        type=str,
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

    log.info(f"Serving on port {server_address[1]}")

    # Start the server in a separate thread
    server_thread: Thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = (
        True  # Allows the program to exit if the main thread terminates
    )
    server_thread.start()
    log.info("Server running in a separate thread.")
    server_thread.join()
    httpd.shutdown()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_arguments()
    run_server(
        port=args.port,
    )


if __name__ == "__main__":
    main()
