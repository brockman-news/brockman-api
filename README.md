
# Brockman API Service

The Brockman API Service is a simple multithreaded HTTP server that listens for POST requests and sends messages to an IRC channel. This service is designed to facilitate communication with an IRC server by posting messages to a specified channel.

## Features

- Multithreaded HTTP server for handling multiple requests concurrently.
- Sends messages to an IRC channel based on the received POST request data.
- Configurable server port, IRC server, and control channel.

## Requirements

- Nix package manager

## Usage

To run the Brockman API Service, use the following command:
```sh
nix run . -- --port <PORT> --irc-server <IRC_SERVER> --control-channel <CONTROL_CHANNEL>
```

### Command-Line Arguments

- `--port`: Port number for the server to listen on (default: 8080).
- `--irc-server`: Hostname of the IRC server (default: brockman.news).
- `--control-channel`: Channel to send control messages to (default: #all).


### Example

```sh
nix run . -- --port 8080 --irc-server brockman.news --control-channel '#all'
```

## API Endpoints

### POST /

Send a message to the IRC channel.

#### Request Body

```json
{
  "feed": "https://www.example.com/rss",
  "nick": "example"
}
```

#### Response

- `200 OK`: Message sent successfully.
- `404 Not Found`: Invalid request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
