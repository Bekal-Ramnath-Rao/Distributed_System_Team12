import argparse
import socket
import sys

def start_client(host, port, message):
    """Start a client to connect to the server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print(f"Connected to server at {host}:{port}")
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")
            response = client_socket.recv(1024)
            print(f"Received: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Client error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Simple Python Client")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server IP address")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--message", type=str, required=True, help="Message to send to the server")

    args = parser.parse_args()
    start_client(args.host, args.port, args.message)

if __name__ == "__main__":
    main()
