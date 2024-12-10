import argparse
import socket
import sys


def start_server(host, port):
    """Start a simple echo server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen(5)
            print(f"Server listening on {host}:{port}")
            
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection received from {client_address}")
                with client_socket:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        print(f"Received: {data.decode('utf-8')}")
                        client_socket.sendall(data)  # Echo data back to client
                        print(f"Sent: {data.decode('utf-8')}")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)



def main():
    print("Server here")
    parser = argparse.ArgumentParser(description="Simple Python Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")

    args = parser.parse_args()
    start_server(args.host, args.port)

main()

if __name__ == "__main__":
    main()
