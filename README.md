# Goto URL Shortener

Goto is a simple URL shortener service implemented in Python. This project provides a multithreaded HTTP server to shorten URLs and retrieve the original URLs.

## Features

- Configurable hash algorithm and length
- In-memory caching of shortened URLs
- Persistent storage of shortened URLs

## Configuration Options

The following options can be configured via command-line arguments:

- `--port`: Port number for the server to listen on (default: `8080`).
- `--hash-algorithm`: Hash algorithm to use for content hashing (default: `sha256`).
- `--hash-length`: Length of the hash to generate (default: `5`).
- `--state-dir`: Location where to store the shortened URLs (default: `goto_state`).
- `--cache-size`: Number of URLs to cache in memory (default: `100`).

## Example Configuration

Here is an example command to run the Goto service with custom configuration:

```sh
python goto/server.py --port 8080 --hash-algorithm sha256 --hash-length 6 --state-dir /path/to/state --cache-size 200
```

## Running the Service

### Without Nix

To run the Goto service without Nix, follow these steps:

1. **Install Dependencies**: Ensure you have Python installed. Install any required dependencies using `pip` if necessary.

2. **Run the Server**: Use the following command to start the server:

    ```sh
    python goto/server.py --port 8080 --hash-algorithm sha256 --hash-length 5 --state-dir goto_state --cache-size 100
    ```

3. **Access the Service**: The server will be running on the specified port (default: `8080`). You can use HTTP POST requests to shorten URLs and HTTP GET requests to retrieve the original URLs.

### With NixOS Module

The following options can be configured in the NixOS module:

- `services.goto.enable`: Enable or disable the Goto service (default: `false`).
- `services.goto.package`: The package to use for the Goto service (default: `./default.nix`).
- `services.goto.port`: The port on which the Goto service will listen (default: `7331`).
- `services.goto.hashAlgorithm`: The hash algorithm to use for generating shortened URLs (default: `sha256`).
- `services.goto.hashLength`: The length of the hash that Goto generates (default: `5`).
- `services.goto.cacheSize`: The number of entries to cache in memory (default: `100`).
- `services.goto.openFirewall`: Open the port in the firewall (default: `false`).

#### Example Configuration

Here is an example configuration for enabling and configuring the Goto service in NixOS:

```nix
{
  services.goto = {
    enable = true;
    port = 8080;
    hashAlgorithm = "sha256";
    hashLength = 6;
    cacheSize = 200;
    openFirewall = true;
  };
}
```

#### Running the Service

Once configured, the Goto service can be started and managed using systemd:

```sh
sudo systemctl start goto
sudo systemctl enable goto
```

## Example Usage

### Shorten a URL

To shorten a URL, send a POST request with the URL in the request body:

```sh
curl -X POST -d "http://example.com" http://localhost:8080
```

### Retrieve the Original URL

To retrieve the original URL, send a GET request with the shortened URL hash:

```sh
curl -X GET http://localhost:8080/<hash>
```

